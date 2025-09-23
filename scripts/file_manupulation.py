import os

def find_folder(folder_name):
    # Search for folder in the whole system
    found_paths = []
    for root, dirs, files in os.walk("/"):
        if folder_name in dirs:
            found_paths.append(os.path.join(root, folder_name))
    return found_paths

def main():
    folder_name = input("Enter the folder name to search: ").strip()
    folder_paths = find_folder(folder_name)
    
    if folder_paths:
        print(f"✅ Folder '{folder_name}' is present at:")
        for path in folder_paths:
            print(f"   {path}")
        folder_path = folder_paths[0]  # Take the first found path
    else:
        print(f"❌ Folder '{folder_name}' not found in the system.")
        return

    print("\nWhat do you want to do?")
    print("1. Create a new file")
    print("2. Write in an existing file")

    choice = input("Enter choice (1/2): ").strip()

    if choice == "2":
        files = os.listdir(folder_path)
        if not files:
            print("No existing files. Please create a new file.")
            return
        
        print("\nExisting files:")
        for i, f in enumerate(files, 1):
            print(f"{i}. {f}")
        file_choice = int(input("Choose a file number: ")) - 1
        if file_choice < 0 or file_choice >= len(files):
            print("Invalid choice!")
        else:
         file_path = os.path.join(folder_path, files[file_choice])
        
         content = input("Enter content to append: ")
         with open(file_path, "a") as f:
            f.write(content + "\n")
         print(f"✅ Content appended to {file_path}")

    elif choice == "1":
        filename = input("Enter file name (without extension): ").strip()
        extension = input("Enter extension (e.g. py, java, js): ").strip()
        content = input("Enter content for the new file: ")

        file_path = os.path.join(folder_path, f"{filename}.{extension}")
        with open(file_path, "w") as f:
            f.write(content + "\n")
        print(f"✅ New file created: {file_path}")

    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
