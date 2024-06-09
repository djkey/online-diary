import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import Lessons from './components/Lessons';
import Homeworks from './components/Homeworks';

const App = () => {
    return (
        <Router>
            <Switch>
                <Route path="/login" component={Login} />
                <Route path="/register" component={Register} />
                <Route path="/profile" component={Profile} />
                <Route path="/lessons" component={Lessons} />
                <Route path="/homeworks" component={Homeworks} />
            </Switch>
        </Router>
    );
};

export default App;
