
import React, { useState } from 'react';
import {formatDate} from '../utils'
import {Button} from 'react-bootstrap'
class JobManagerProps {
    public loading!: boolean;
    public setLoading!: Function;
}
function JobManager(props: JobManagerProps) {
    function requestCalculation() {
        props.setLoading(true);
        // imitate the request to the db
        console.log("Requesting processing...")
        setTimeout(props.setLoading(false),2000); 
    }
    const nextCalcTime = getNextScheduledCalculationTime();
    return (
    <div className="row-fluid"style={{marginBottom:"20px", marginTop:"20px"}}>
        <h2>Наступна обробка о: {formatDate(nextCalcTime)}</h2>
        <Button  onClick={requestCalculation} disabled={props.loading}> Запустити обробку зараз</Button>
    </div>)
}
function getNextScheduledCalculationTime() {
    let date = new Date();
    date.setUTCHours(date.getUTCHours()- 7);
    const now = new Date();
    while (now > date) {
        date.setDate(date.getDate() + 1); //why 1, though?
    }
    return date;
}

export {JobManager}
