from bs4 import BeautifulSoup


class PrettyXML():
    def __init__(self, xml):
        """
        make xml pretty
        needs BeautifulSoup to make use of this
        pip install beautilfulsoup4
        """
        self.xml = xml
    
    def make_pretty(self) -> list:
        """
        make xml pretty with beautifulsoup
        there will be some formatting issues that we need to file
        - output:
            - list of xml elements
        """
        soup = BeautifulSoup(self.xml, "xml")
        return soup.prettify().split("\n")[1:] # remove first line, contains added version line
    
    def format_string(self, i, pretty) -> str:
        """
        format string for previous index to hold
        - input
            - i: index of string we are appending to previous string
            - pretty: list of xml elements
        - output
            string to be put into previous element
        """
        pretty[i] = pretty[i].replace("&gt;", ">")        
        pretty[i] = pretty[i].strip() # remove whitespace
        return "{0}{1}".format(pretty[i-1][:-1], pretty[i]) # append previous index with current

    def remove_indices(self, indices_not_needed, pretty) -> str:
        """
        remove the lines we appended to the line above it
        - input:
            - indices_not_needed: list of indices that we can remove from pretty list
            - pretty: list of xml elements that have already been formatted
        - output:
            - correctly formated string of xml elements
        """
        for index in indices_not_needed[::-1]:
            pretty.pop(index)
        return "\n".join(pretty)

    def fix_formatting(self) -> str:
        """
        fixing beautiful formatting that we don"t like
        - output:
            - return new pretty xml to be printed on website
        """
        pretty = self.make_pretty()
        indices_not_needed = list()
        for i in range(len(pretty)):
            if "=" in pretty[i] and "&gt;" in pretty[i]:
                pretty[i-1] = self.format_string(i, pretty)
                indices_not_needed.append(i)
        return self.remove_indices(indices_not_needed, pretty)

    def get(self) -> str:
        """
        get formatted xml
        """
        return self.fix_formatting()