# Simple Python file handling

def write_file():
    """Write text to a file."""
    with open("test.txt", "w") as f:
        f.write("Hello, this is a practice file!\n")
    print("File created: test.txt")

def read_file():
    """Read and display the file content."""
    try:
        with open("test.txt", "r") as f:
            content = f.read()
        print("\nFile content:")
        print(content)
    except FileNotFoundError:
        print("File not found. Please create it first.")

# Simple menu for user interaction
print("1. Create File")
print("2. Read File")

choice = input("Enter your choice: ")

if choice == "1":
    write_file()
elif choice == "2":
    read_file()
else:
    print("Invalid choice.")
