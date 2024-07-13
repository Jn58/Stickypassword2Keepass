"""
s2k (Sticky password to Keepass)

Convert xml file exported from stick password to csv file for keepass

Example:
    If xml file name is default.xml
    ```
    python s2k.py
    ```

    If xml file name is 'password.xml'
    ```
    python s2k.py password.xml
    ```

    Specify csv file name
    ```
    python s2k.py -o out.csv
    ```
    ```
    python s2k.py password.xml out.csv
    ```
"""

import xml.etree.ElementTree as ET
import argparse


def xml2csv(file: str = "default.xml"):
    """
    Yield comma-separated login information for KeePass from a Sticky Password XML file.

    Args:
        file: XML file path exported from Sticky Password.

    Yields:
        Comma-separated login information string for KeePass.
    """

    tree: ET.ElementTree = ET.parse(file)

    database: ET.Element | None = tree.find("Database")
    assert isinstance(database, ET.Element)

    accounts: ET.Element | None = database.find("Accounts")
    assert isinstance(accounts, ET.Element)
    logins: ET.Element | None = database.find("Logins")
    assert isinstance(logins, ET.Element)
    groups: ET.Element | None = database.find("Groups")
    assert isinstance(groups, ET.Element)

    id_group = {x.attrib["ID"]: x for x in groups}
    id_account = {x.attrib["ID"]: x for x in accounts}
    sourceid_login = {
        x.attrib["SourceLoginID"]: x for x in accounts.findall(".//Login")
    }

    for login in logins:
        account_login = sourceid_login[login.attrib["ID"]]
        account = id_account[account_login.attrib["ParentID"]]
        group = id_group.get(account.attrib["ParentID"], None)

        group = group.attrib["Name"] if group is not None else ""
        title = account.attrib["Name"]
        username = login.attrib["Name"]
        password = login.attrib["Password"]
        url = account.attrib["Link"]
        last_modified = login.attrib["ModifiedDate"]
        created = login.attrib["CreatedDate"]

        yield f"{group},{title},{username},{password},{url},{last_modified},{created}\n"


def main(xml_file, csv_file):
    """
    Convert XML to CSV and write into a CSV file.
    """
    with open(csv_file, "w", encoding="UTF-8") as f:
        f.write("group,title,username,password,url,last modified,created\n")
        f.writelines(xml2csv(xml_file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Sticky Password XML file to CSV file for KeePass"
    )

    parser.add_argument(
        "input_file",
        type=str,
        nargs="?",
        default="default.xml",
        help="Input file (default: default.xml)",
    )

    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        default="keepass.csv",
        help="Output file (default: keepass.csv)",
    )

    parser.add_argument(
        "-i", "--input", type=str, help="Input file (overrides positional inputfile)"
    )

    parser.add_argument(
        "-o", "--output", type=str, help="Output file (overrides positional outputfile)"
    )

    args = parser.parse_args()

    input_file = args.input if args.input else args.input_file
    output_file = args.output if args.output else args.output_file

    main(input_file, output_file)
