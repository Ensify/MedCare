import React, { useState, useEffect } from "react";
import "../css/Summary.css";
// import Header from "./components/Header";
import Card from "./Card";
import { useParams } from "react-router-dom";
import axios from "axios";

const Summary = () => {
  const { id } = useParams();
  console.log(id);
  // const [record, setRecord] = useState(null);
  const [complexWords, setComplexwords] = useState([]);
  const [meanings, setMeanings] = useState([]);
  const [summaryText, setSummaryText] = useState("");

  useEffect(() => {
    const fetchRecord = async () => {
      try {
        const record = await axios.get(
          `http://13.201.194.131:5000/patientrecord/conv-summary/${id}`
        );
        setSummaryText(record.data.patientSummary.summaryText);
        setComplexwords(record.data.patientSummary.indices);
        setMeanings(record.data.patientSummary.meanings);
      } catch (error) {
        console.error("Error fetching record:", error);
      }
    };

    fetchRecord();
  }, [id]);

  const [speaking, setSpeaking] = useState(false);
  const [cardWord, setCardWord] = useState("");
  const [cardMeaning, setCardMeaning] = useState("");

  const synth = window.speechSynthesis;

  const displayCard = (word, e) => {
    e.preventDefault();
    // const wordIndex = complexWords.indexOf(word.toLowerCase());
    setCardWord(
      summaryText.substring(complexWords[word][0], complexWords[word][1])
    );
    setCardMeaning(meanings[word]);
  };

  const speak = () => {
    if (synth.speaking) {
      return;
    }

    const utterance = new SpeechSynthesisUtterance(summaryText);
    synth.speak(utterance);
    setSpeaking(true);

    utterance.onend = () => {
      setSpeaking(false);
    };
  };
  let start = 0;
  console.log(summaryText);
  return (
    <div style={{ backgroundColor: "#dcf2f1" }} className="summary-page">
      {/* <Header /> */}
      <div className="summary-content container">
        <div className="row text-start">
          <div className="col-lg-8 summary-text text-justify px-4">
            {complexWords.map((pos, index) => {
              const startIdx = pos[0];
              const endIdx = pos[1];
              const highlightedWord = summaryText.substring(startIdx, endIdx);
              const precedingText = summaryText.substring(start, startIdx);
              start = endIdx;

              return (
                <span key={index}>
                  {precedingText}
                  <span
                    className="highlighted-text"
                    onClick={(e) => displayCard(index, e)}
                  >
                    {highlightedWord}
                  </span>
                </span>
              );
            })}
            {summaryText.substring(start)}
            <br />
            <button
              onClick={speak}
              disabled={!summaryText || speaking}
              className="speak-button"
            >
              Speak text
            </button>
          </div>
          <div className="col-lg-4">
            {cardWord && <Card word={cardWord} meaning={cardMeaning} />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Summary;
