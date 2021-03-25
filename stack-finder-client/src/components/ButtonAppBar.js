import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import AccountCircle from '@material-ui/icons/AccountCircle';
import CloudIcon from '@material-ui/icons/Cloud';


const styles = theme => ({
    root: {
        flexGrow: 1,
    },
    menuButton: {
        marginRight: theme.spacing(1),
    },
    title: {
        flexGrow: 1,
        '& > a': {
            textDecoration: 'none',
            color: 'inherit'
        }
    },
    user: {
        flexGrow: 1,
        align: "center",
        display: "inline-block"
    },
    account_circle: {
        float: "left",
        marginRight: theme.spacing(2)
    },
});

class ButtonAppBar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: []
        };
    }

    async componentDidMount() {
        document.title = "StackFinder";
        const username = await fetch("/stacks-api/user");
        const user_json = await username.json();
        if (window.location.href.indexOf("login") > -1) {
            user_json.user = "";
        }
        else if (user_json.user == "error") {
            window.location.href = "https://"+window.location.host+"/stacks/error";
        }
        this.setState({
            user: user_json.user
        });
    }

    render() {
        const classes = this.props.classes;
        return (
            <div className={classes.root}>
                <AppBar position="static">
                    <Toolbar>
                        <CloudIcon className={classes.menuButton}/>
                        <Typography variant="h6" className={classes.title}>
                            <a href="/stacks">Stack Finder</a>
                        </Typography>
                        <div className={classes.user}>
                            <AccountCircle className={classes.account_circle}/>
                            <Typography variant="h7">{this.state.user}</Typography>
                        </div>
                        <Button color="inherit" href="https://awslogin.pnl.gov">AWS Login</Button>
                        <Button color="inherit" href="/stacks/logout">Logout</Button>
                    </Toolbar>
                </AppBar>
            </div>
        );
    }
}

export default withStyles(styles)(ButtonAppBar);
