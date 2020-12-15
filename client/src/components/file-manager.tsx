
import React, { useState } from 'react';
import { FileDto } from '../domain/file.dto';
import { Button } from 'react-bootstrap'
import {formatDate} from '../utils'
class FileManagerProps{
 public files!: FileDto[]
 public setFiles!: Function
 public loading!: boolean
 public setLoading!: Function
}
function FileManager(props: FileManagerProps){
    function uploadFile(file: any) {
        props.setLoading(true);
        // imitate the request to the db
        console.log("Uploading file...")
        setTimeout(props.setLoading(false),2000); 
    }
  const fileItems = props.files.map(f => 
  <tr key={f.name}>
    <td><a href="#">{f.name}</a></td>
    <td>{f.size}</td>
    <td>{formatDate(f.lastModified)}</td>
    <td><Button variant="danger" disabled={props.loading}>Видалити</Button></td>
  </tr>);

  return (
      <div className="row-fluid">
    <div >
    <h2>
        Файли у сховищі конфігурацій:
    </h2>
        <table className="table">
            <thead>
                <tr>
                <th scope="col">Назва</th>
                <th scope="col">Розмір (байти)</th>
                <th scope="col">Востаннє змінено</th>
                <th scope="col">Дії</th>
                </tr>
            </thead>
            <tbody>
                {fileItems}
            </tbody>
        </table>
        <div className="row-fluid">
            <Button  onClick={uploadFile} disabled={props.loading}> Завантажити новий файл</Button>
        </div>
    </div>
    </div>
  );
}


export {FileManager};
