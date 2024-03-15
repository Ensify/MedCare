import React from "react";
import "../css/Card.css";

const Card = ({ word, meaning }) => {
  return (
    <div className="card explain-card">
      <h5 className="card-header">
        <span className="card-word">{word}</span>
      </h5>
      <div className="card-body">
        {/* <h5 className="card-title">{meaning}</h5> */}
        <p className="card-text">{meaning}</p>
        {/* <a href="#" className="btn btn-primary">Go somewhere</a> */}
      </div>
    </div>
  );
};

export default Card;
