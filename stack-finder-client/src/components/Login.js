import React, { useEffect, useState } from 'react';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import Link from '@material-ui/core/Link';
import Box from '@material-ui/core/Box';
import Paper from '@material-ui/core/Paper';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="https://material-ui.com/">
        Stack Finder
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '4rem'
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));

const Login = () => {
  const [hasError, setErrors] = useState(false);
  const [authUrl, setAuthUrl] = useState('');
  const classes = useStyles();

  // Define fetch data function
  async function fetchData() {
    const res = await fetch('/stacks-api/login');
    res
      .json()
      .then(res => setAuthUrl(res.authUrl))
      .catch(err => setErrors(err));
  }

  // Fetch on mount
  useEffect(() => {
    document.title = "StackFinder";
    fetchData();
  },[]);

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <Paper className={classes.paper} elevation={1}>
        <Avatar className={classes.avatar}>
          <LockOutlinedIcon />
        </Avatar>
        <Button
          href={authUrl !== '' ? authUrl : ''}
          fullWidth
          variant="contained"
          color="primary"
        >
          <Typography component="h1" variant="h5">
            Sign in
          </Typography>
        </Button>
      </Paper>
      <Box mt={8}>
        <Copyright />
      </Box>
    </Container>
  );
}

export default Login;
