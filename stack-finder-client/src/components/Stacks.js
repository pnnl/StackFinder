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

class Stacks extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            isloaded: false,
            data: []
        };
    }

    async componentDidMount() {
        document.title = "StackFinder";

        function createData(group, stack, deployment_date, build_tag, link) {
            return { group, stack, deployment_date, build_tag, link };
        }

        const resp = await fetch("/stacks-api/stacks");
        const json = await resp.json();
        if (json.stacks == "error") {
            window.location.href = "https://"+window.location.host+"/stacks/error";
        } else if (json.stacks == "login") {
            //window.location.href = "https://"+window.location.host+"/stacks/login";
        }
        var items = [];
        for (var i = 0; i < json.stacks.length; i++) {
            items.push(createData(
                json.stacks[i].group, 
                json.stacks[i].stack, 
                json.stacks[i].deployment_date,
                json.stacks[i].build_tag.replace(/=/g, ' | '), 
                "/stacks/"+json.stacks[i].stack
            ))
        }
        this.setState({
            isloaded: true,
            data: items
        });
    }

    render() {
        const classes = this.props.classes;
        const rows = this.state.data;
        console.log(rows);
        if (!this.state.isloaded) {
            return (
                <CircularProgress className={classes.circle} />
            );
        } else {
            return (
                <TableContainer component={Paper}>
                    <Table className={classes.table} aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                <TableCell>Group</TableCell>
                                <TableCell>Stack</TableCell>
                                <TableCell>Deployment Date</TableCell>
                                <TableCell>Build Tag</TableCell>
                                <TableCell></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {rows.map((row) => (
                                <TableRow key={row.stack}>
                                    <TableCell component="th" scope="row">
                                        {row.group}
                                    </TableCell>
                                    <TableCell component="th" scope="row">
                                        {row.stack}
                                    </TableCell>
                                    <TableCell component="th" scope="row">
                                        {row.deployment_date}
                                    </TableCell>
                                    <TableCell component="th" scope="row">
                                        {row.build_tag}
                                    </TableCell>
                                    <TableCell component="th" scope="row">
                                        <Button className={classes.button} variant="contained" color="primary" href={row.link}>View</Button>
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

export default withStyles(styles)(Stacks);
