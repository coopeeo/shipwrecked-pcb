import React, { use, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import ConnectionSettings from './components/ConnectionSettings';
import { MicroPythonProvider } from './MicroPythonContext';
import BadgeConfigurator from './components/BadgeConfigurator';

function App() {
  useEffect(() => {
    document.title = 'Shipwrecked PCB flasher';
  }, []);
  return (
    <MicroPythonProvider>
      <div className="App">
        <ConnectionSettings />
        <BadgeConfigurator />
      </div>
    </MicroPythonProvider>
  );
}

export default App;
