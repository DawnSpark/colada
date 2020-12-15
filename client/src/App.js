import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.css';

import { FileManager } from './components/file-manager';
import { JobManager } from './components/job-manager'
import React, { useState } from 'react';
import { FileService } from './services/file.service';

function App() {
  const fileService = new FileService();
  const [loading, setLoading] = useState(false);

  const [files, setFiles] = useState(fileService.getFiles() || []);
  //imitate loading 
  //setLoading(false);
  return (
    <div className="App">
    <div className=" d-flex justify-content-center">
      <JobManager loading={loading} setLoading={setLoading} />
      </div>
      <div className="d-flex justify-content-center">
      <FileManager files={files} setFiles={setFiles} loading={loading} setLoading={setLoading} />
      </div>
    </div>
  );
}

export default App;
// <div className="App">
    //   <header className="App-header">
    //   </header>
    // </div>