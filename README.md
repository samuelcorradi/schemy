# Schemy

Data structure to represent schemas in databases.

# Change history

**0.1.4**

- Added the format property to the Field object.

- Support for date and datetime types.

- SQL command generation is now separated into a specific class, instead of being methods of the Schema class.

**0.1.3**

- Removed the need for the schema to have a name to represent the repository name. The schema will only define the internal structure (fields, keys, constraints, etc.) from here on out.