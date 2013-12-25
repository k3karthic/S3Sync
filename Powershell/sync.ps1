$files = Get-Content -Raw ../config/files.json | ConvertFrom-Json
$config = Get-Content -Raw ../config/credentials.json | ConvertFrom-Json
$encoding = [System.Text.Encoding]::UTF8
$sha512 = New-Object System.Security.Cryptography.SHA512CryptoServiceProvider
$s3files = @{}

Function unixTimestamp($date) {
    $epoch = $date.ToUniversalTime().Ticks
    $epoch = $epoch - 621355968000000000
    $epoch = $epoch / 10000000

    return [Math]::floor($epoch)
}

Function convertS3Key($dirsub,$path,$alias) {
    $subpath = $path.Substring($path.IndexOf($dirsub))

    if($alias.Length -gt 0) {
        $subpath = $subpath.Replace($dirsub,$alias)
    }

    return $subpath
}

$rrs = ""
$encrypt = ""

if($config.rrs -eq 1) {
    $rrs = "-ReducedRedundancyStorage"
}

if($config.encrypt -eq 1) {
    $encrypt = "-ServerSideEncryption AES256"
}

#
# Traverse S3 Bucket
#
Get-S3Object -BucketName $config.bucket | Foreach-Object {
    $s3key_hash = $encoding.GetString(
        $sha512.ComputeHash($encoding.GetBytes($_.Key))
    )
    
    $s3files.Set_Item($s3key_hash,@{
        'key' = $_.Key;
        'size' = $_.Size;
        'mtime' = ''
    })
}

#
# Retrieve 'Last Modified' date from local store
#
if((Test-Path -Path working/LastSync.txt) -ne $True) {
    "" | Set-Content -Path working/LastSync.txt
}

Get-Content -Path working/LastSync.txt | Foreach-Object {
    if($_.Length -gt 0) {
        $items = $_.split('<>')
    
        $dirsub = $items[0]
        $path = $items[2]
        $mtime = $items[4]
        $alias = $items[6]
    
        if($alias -eq $null) {
            $alias = ""
        }
    
        $s3key = convertS3Key $dirsub $path $alias
        $s3key_hash = $encoding.GetString(
            $sha512.ComputeHash($encoding.GetBytes($s3key))
        )
    
        if($s3files.ContainsKey($s3key_hash)) {
            $s3files.Get_Item($s3key_hash).Set_Item('mtime',$mtime)
        }
    }
}

#
# Traverse Local File System
#
"" | Set-Content -Path working/LastSync.txt

foreach ($i in $files) {
    $dirsub = $i.dir
    $alias = ""
    $excludes = @()
    $rrs_param = $rrs
    $encrypt_param = $encrypt

    if($i.exclude -ne $null) {
        $excludes = $i.exclude
    }

    if($i.alias -ne $null) {
        $alias = $i.alias
    }

    if($i.rrs -ne $null) {
        if($i.rrs -eq 1) {
            $rrs_param = "-ReducedRedundancyStorage"
        } else {
            $rrs_param = ""
        }
    }

    if($i.encrypt -ne $null) {
        if($i.encrypt -eq 1) {
            $encrypt_param = "-ServerSideEncryption AES256"
        } else {
            $encrypt_param = ""
        }
    }

    Get-ChildItem -Path $i.path -Recurse | Foreach-Object {
        if($_.Length -ne 1) {
            $valid = $True
            $path = $_.FullName
            $size = $_.Length
            $mtime = unixTimestamp $_.LastWriteTime
            $unix_path = $path -replace '\\','/'

            Add-Content working/LastSync.txt "$dirsub<>$path<>$mtime<>$alias"
    
            foreach ($e in $excludes) {
                if($unix_path -Match $e) {
                    $valid = $False
                    break
                }
            }
    
            if($valid) {
                $unix_path = convertS3Key $dirsub $unix_path $alias

                $unix_path_hash = $encoding.GetString(
                    $sha512.ComputeHash($encoding.GetBytes($unix_path))
                )
    
                if($s3files.ContainsKey($unix_path_hash)) {
                    $obj = $s3files.Get_Item($unix_path_hash)
    
                    if($obj.mtime.Length -eq 0) {
                        $obj.mtime = $mtime
                    }
    
                    if(($obj.mtime -ne $mtime) -or ($obj.size -ne $size)) {
                        Write-Output "Update file: $path"
                        $esc_path = $path -replace ' ','` '
                        $esc_key = $unix_path -replace ' ','` '
                        $cmd = "Write-S3Object -BucketName $($config.bucket) -File $esc_path -Key $esc_key $rrs_param $encrypt_param"
                        Invoke-Expression $cmd
                    }

                    $s3files.Remove($unix_path_hash)
                } else {
                    Write-Output "New file: $path"
                    $esc_path = $path -replace ' ','` '
                    $esc_key = $unix_path -replace ' ','` '
                    $cmd = "Write-S3Object -BucketName $($config.bucket) -File $esc_path -Key $esc_key $rrs_param $encrypt_param"
                    Invoke-Expression $cmd

                    $s3files.Remove($unix_path_hash)
                }
            }
        }
    }
}

foreach ($h in $s3files.GetEnumerator()) {
    $s3key = $h.Value.Get_Item('key')

    if($s3key.Substring($s3key.Length - 1) -ne '/') {
        Write-Output "Delete file: $s3key"
    
        $esc_key = $s3key -replace ' ','` '
        $cmd = "Remove-S3Object -BucketName $($config.bucket) -Key $esc_key -Force"
        $output = Invoke-Expression $cmd
    }
}
