import React from 'react';
import { withStyles } from '@material-ui/styles';
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Container, CircularProgress } from '@material-ui/core';

const styles = theme => ({
    table: {
        minWidth: 650,
    },
    button: {
        float: 'right',
    },
    circle: {
        marginLeft: 'auto',
        marginRight: 'auto',
        display: 'block',
        width: 50,
        position: 'relative',
    }
});

class Outputs extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: props.name,
            isloaded: false,
            data: [],
            bucket: "",
            logs: "",
            webservice: ""
        };
    }

    async componentDidMount() {
        document.title = "StackFinder";
        const resp = await fetch("/stacks-api/outputs?stackname="+this.props.name);
        const json = await resp.json();
        
        for (var i = 0; i < json.Outputs.length; i++) {
            if ((json.Outputs[i].ExportName != null && json.Outputs[i].ExportName.toLowerCase().includes("bucket")) || json.Outputs[i].OutputKey.toLowerCase().includes("bucket")) {
                var bucket = await fetch("/stacks-api/outputs/bucket?bucketname="+json.Outputs[i].OutputValue);
                var bucket_json =  await bucket.json();
                if (bucket_json["bucket-url"] == "error") {
                    window.location.href = "https://"+window.location.host+"/stacks/error";
                } else if (bucket_json["bucket-url"] == "login") {
                    window.location.href = "https://"+window.location.host+"/stacks/login";
                }
                this.setState({bucket: bucket_json["bucket-url"]});
            } else if (((json.Outputs[i].ExportName != null && json.Outputs[i].ExportName.toLowerCase().includes("webservicename")) || json.Outputs[i].OutputKey.toLowerCase().includes("webservicename")) ||
                ((json.Outputs[i].ExportName != null && json.Outputs[i].ExportName.toLowerCase().includes("loaderservicename")) || json.Outputs[i].OutputKey.toLowerCase().includes("loaderservicename"))) {
                var service = await fetch("/stacks-api/outputs/servicepage?servicename="+json.Outputs[i].OutputValue+"&clustername=ardis-n25-dc");
                var service_json = await service.json();
                if (service_json["service-page-url"] == "error") {
                    window.location.href = "https://"+window.location.host+"/stacks/error";
                } else if (service_json["service-page-url"] == "login") {
                    window.location.href = "https://"+window.location.host+"/stacks/login";
                }
                this.setState({webservice: service_json["service-page-url"]});
            } else if ((json.Outputs[i].ExportName != null && json.Outputs[i].ExportName.toLowerCase().includes("log")) || json.Outputs[i].OutputKey.toLowerCase().includes("log")) {
                var log = await fetch("/stacks-api/outputs/logs?logname="+json.Outputs[i].OutputValue);
                var log_json = await log.json();
                if (log_json["log-url"] == "error") {
                    window.location.href = "https://"+window.location.host+"/stacks/error";
                } else if (log_json["log-url"] == "login") {
                    window.location.href = "https://"+window.location.host+"/stacks/login";
                }
                this.setState({logs: log_json["log-url"]});
            }
        }

        this.setState({
            isloaded: true,
            data: json
        });
    }

    render() {
        const classes = this.props.classes;
        if (!this.state.isloaded) {
            return (
                <CircularProgress className={classes.circle} />
            )
        } else {
            return (
                <TableContainer component={Paper}>
                    <Table className={classes.table} aria-label="simple-label">
                        <TableHead>
                            <TableRow>
                                <TableCell>
                                    {this.props.name}
                                </TableCell>
                                <TableCell>
                                    <Button className={classes.button} variant="contained" color="primary" href={"https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/stackinfo?filteringText=&filteringStatus=active&viewNested=true&hideStacks=false&stackId="+this.props.name}>CloudFormation</Button>
                                </TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Key</TableCell>
                                <TableCell>Value</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {this.state.data.Outputs.map(el => (
                                <TableRow>
                                    <TableCell component="th" scope="row">
                                        { (el.ExportName!=null) ? el.ExportName : el.OutputKey }
                                    </TableCell>
                                    <TableCell component="th" scope="row">
                                        {el.OutputValue}
                                        {(function(el, state) { 
                                            if ((el.ExportName != null && el.ExportName.toLowerCase().includes("bucket")) || el.OutputKey.toLowerCase().includes("bucket")) {
                                                return <Button className={classes.button} variant="contained" color="primary" href={state.bucket}>AWS</Button>;
                                            } else if (((el.ExportName != null && el.ExportName.toLowerCase().includes("webservicename")) || el.OutputKey.toLowerCase().includes("webservicename")) ||
                                            ((el.ExportName != null && el.ExportName.toLowerCase().includes("loaderservicename")) || el.OutputKey.toLowerCase().includes("loaderservicename"))){
                                                return <Button className={classes.button} variant="contained" color="primary" href={state.webservice}>AWS</Button>;
                                            } else if ((el.ExportName != null && el.ExportName.toLowerCase().includes("log")) || el.OutputKey.toLowerCase().includes("log")) {
                                                return <Button className={classes.button} variant="contained" color="primary" href={state.logs}>AWS</Button>;
                                            } else if ((el.ExportName != null && el.ExportName.toLowerCase().includes("bamboolink") || el.OutputKey.toLowerCase().includes("bamboolink"))) {
                                                return <Button className={classes.button} variant="contained" color="primary" href={el.OutputValue}>Bamboo</Button>
                                            }
                                        }(el, this.state))}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            );
        }
    }
}


export default withStyles(styles)(Outputs);
