import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Router } from "@reach/router";
import { Container } from '@material-ui/core';
import { ButtonAppBar, Login, Stacks, Outputs } from './components';
import './App.css';

const useStyles = makeStyles({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: '4rem',
    display: 'flex',
    height: '100%',
    width: '100%',
    maxWidth: '1500px'
  },
  router: {
    paddingTop: '4rem',
    verticalAlign: 'center',
    height: '100%',
    width: '100%',
  }
});

const App = () => {
  const classes = useStyles();
  return (
    <>
      <ButtonAppBar/>
      <Container className={classes.container}>
          <Router className={classes.router}>
            <Login path="/stacks/login" />
            <Outputs path="/stacks/:name" />
            <Stacks path="/stacks" />
          </Router>
      </Container>
    </>
  );
}

export default App;
