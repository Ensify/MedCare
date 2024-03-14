import DataTable from "react-data-table-component";
import "../css/Records.css";
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link, useParams } from "react-router-dom";

const customStyles = {
  rows: {
    style: {
      minHeight: "72px", // override the row height
      backgroundColor: "#F1FADA",
    },
  },
  headCells: {
    style: {
      paddingLeft: "8px", // override the cell padding for head cells
      paddingRight: "8px",
      fontSize: "1.3em",
      fontWeight: "bolder",
      backgroundColor: "#2D9596",
    },
  },
  cells: {
    style: {
      paddingLeft: "8px", // override the cell padding for data cells
      paddingRight: "8px",
    },
  },
};

const Records = () => {
  const { patientId } = useParams();
  const [records, setRecords] = useState([]);

  const columns = [
    {
      name: "Doctor Consulted",
      selector: (row) => row.doctorName,
    },
    // {
    //   name: "Hospital",
    //   selector: (row) => row.hospital,
    // },
    {
      name: "Visited On",
      selector: (row) => row.Date,
    },
    //   {
    //     name: "Type",
    //     selector: (row) => row.type,
    //   },
    {
      name: "View",
      cell: (row) => (
        <Link to={`/patientsum/${row._id}`}>
          {console.log(row._id)}
          <button className="btn btn-primary">View</button>
        </Link>
      ),
    },
  ];

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const response = await axios.get(
          `http://13.201.194.131:5000/conv-summary/${patientId}`
        );
        response.data.forEach((data) => {
          console.log(data._id);
        });
        setRecords(response.data);
      } catch (error) {
        console.error("Error fetching records:", error);
      }
    };

    fetchRecords();
  }, [patientId]);

  return (
    <div className="table-box">
      <DataTable
        title="Available Reports"
        columns={columns}
        data={records.map((record) => ({
          doctorName: record.doctorName,
          //   hospital: record.hospital,
          Date: record.Date,
          _id: record._id,
        }))}
        pagination
        customStyles={customStyles}
        className="table"
      />
    </div>
  );
};

export default Records;
