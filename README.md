# Componentn Builder

This is the builder used to determine what needs to be tested and deployed.

## Entry points

### build

 - Figure out which components have changed
 - Run their build scripts

### test

 - Figure out which components have changed
 - Run their test scripts

### release

- Figure out which components have changed
- Release those that require releasing


## Development

$ pip install -e builder

Now you can play with it!

## Configuring

`builder.ini`, found in the working directory from which you run
`compbuild build` holds configuration for the build process.

Each component that needs building, testing and releasing should be defined
there.
