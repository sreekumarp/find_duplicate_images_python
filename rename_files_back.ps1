# Get all files in the current directory and its subfolders
$files = Get-ChildItem -Recurse -File

# Loop through each file
foreach ($file in $files) {
    # Extract the filename without extension
    $filenameWithoutExt = $file.BaseName

    # Define the patterns to match
    $patterns = @("_Dupli", "_Orig","_Orig1", "_Orig2","_Orig3","_Orig_Orig", "_Orig_Orig1", "_Orig_Orig2", "_Orig_Orig3")

    # Check if the filename contains any of the patterns
    foreach ($pattern in $patterns) {
        if ($filenameWithoutExt -match $pattern) {
            # Remove the pattern from the filename
            $newFilename = $filenameWithoutExt -replace $pattern, ""

            # Rename the file
            Rename-Item -Path $file.FullName -NewName ("$newFilename" + $file.Extension)

            # Break out of the inner loop after renaming
            break 
        }
    }
}