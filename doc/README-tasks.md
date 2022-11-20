# Common Tasks

## Test if aloha is properly installed

```bash
aloha info
```

This will display the package version information.

## Start a function from the main function EntryPoint

```bash
aloha start package_name.module_name
# e.g.: aloha start app_common.debug
```

Notice: this module_name **MUST** include a function named `main()`.

## Compile Python Code into binary

Sometime, you need to compile your python source code into binary libraries to protect your source code.

Aloha helps you build your python source code into binary using `Cython`. You can run the following command to build your code.

```bash
aloha compile --base=./demo --dist=./build --keep='main.py'
```

The following options can be used:

- `--base`: the root folder which includes source code to build
- `--dist`: (default='build') target folder for the binary code
- `--exclude`: a collection of files/folders to exclude  (you can specify multiple excludes by using this option multiple times) 
- `--keep`: source files keep as is and not converting to dynamic library (you can specify multiple excludes by using this option multiple times)
