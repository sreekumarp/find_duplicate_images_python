# Get all files ending with "_Dupli[1-9].jpg" recursively
#Get-ChildItem -Path "F:\ULTFONE_20240829_175529\E\Lost Files\File Name Lost\jpg\JPG\2024\Processed1\300 x 100_Done" -Filter "*_Dupli[1-9].jpg" -Recurse | 
# Define the folder path where the files are located
$folderPath = "F:\ULTFONE_20240829_175529\E\Lost Files\File Name Lost\jpg\JPG\2024\Processed1\"
# Script to rename folders, change file extensions, and delete empty folders

# Set the $baseDir = "C:\Your\Base\Directory" # Replace with the path to your directorybase directory where the folders are located
$baseDir =$folderPath # Replace with the path to your directory

# Get all directories ending with "_Done_Classified"
$folders = Get-ChildItem -Path $baseDir -Directory -Recurse | Where-Object { $_.Name -like "*_Done_Classified" }

foreach ($folder in $folders) {
    # Get the new folder name by removing the "_Done_Classified" postfix
    $newFolderName = $folder.Name -replace "_Done_Classified$", ""
    $newFolderPath = Join-Path -Path $folder.Parent.FullName -ChildPath $newFolderName

    # Rename the folder
    Rename-Item -Path $folder.FullName -NewName $newFolderName
    Write-Host "Renamed folder: '$($folder.FullName)' to '$newFolderPath'"

    # Check if the renamed folder contains a subfolder named "Error"
    $errorFolder = Join-Path -Path $newFolderPath -ChildPath "Error"
    if (Test-Path -Path $errorFolder -PathType Container) {
        # Get all files inside the "Error" folder
        $files = Get-ChildItem -Path $errorFolder -File
        foreach ($file in $files) {
            # Change the file extension to .xxjgpxx
            $newFileName = "$($file.BaseName).xxjgpxx"
            Rename-Item -Path $file.FullName -NewName $newFileName
            Write-Host "Renamed file: '$($file.FullName)' to '$newFileName'"
        }

        # Delete the "Error" folder if it's empty
        if ((Get-ChildItem -Path $errorFolder -File).Count -eq 0) {
            Remove-Item -Path $errorFolder -Recurse -Force
            Write-Host "Deleted empty folder: '$errorFolder'"
        }
    } else {
        Write-Host "No 'Error' folder found in '$newFolderPath'"
    }

    # Delete the renamed folder if it's empty (after processing "Error" subfolder)
    if ((Get-ChildItem -Path $newFolderPath -Recurse -File).Count -eq 0) {
        Remove-Item -Path $newFolderPath -Recurse -Force
        Write-Host "Deleted empty folder: '$newFolderPath'"
    }
}
