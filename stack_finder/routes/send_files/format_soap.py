from routes.send_files.pretty_xml import PrettyXML
#from pretty_xml import PrettyXML


class FormatSoap():
    def transform_helper(self, item) -> str:
        """
        takes character from string and transforms it use with map
        - input
            - item: char from string
        - output
            - transformed char if needed
        """
        if item == "<":
            return "&lt;"
        elif item == ">":
            return  "&gt;"
        elif item == "\"":
            return "&quot;"
        return item
    
    def parse_soap_response(self, soap) -> str:
        """
        turn soap message into xml data
        - input:
            - soap: soap message returned from server
        - output:
            - xml to be displayed to user
        """
        soap = soap.replace("&lt;", "<")
        soap = soap.replace("&gt;", ">")
        soap = soap.replace("&quot;", "\"")
        return PrettyXML(soap).get()

    def transform_xml(self, data) -> str:
        """
        transform xml to soap xml
        - input
            - data: takes xml data from a file
        - output
            - returns xml that has been formatted for soap
        """
        ldata = list(map(self.transform_helper, data))
        return "".join(ldata)

    def format_soap(self, xml) -> str:
        """
        take formated xml and wrap soap around it
        - input
            - xml: xml that was read from S3
        - output
            - returns soap msg
        """
        formated_xml = self.transform_xml(xml)
        return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\
            <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\
               xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\"\
               xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\
                <soap:Body>\
                    <RecordActivity xmlns=\"http://pride.cbp.dhs.gov\">\
                        <sN25Messages>\
                            <string>\
                                {0}\
                            </string>\
                        </sN25Messages>\
                    </RecordActivity>\
                </soap:Body>\
            </soap:Envelope>".format(
                formated_xml
            )