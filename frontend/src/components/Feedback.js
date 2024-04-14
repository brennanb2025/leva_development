import React, { useState, useEffect } from 'react'
import { Formik, Field, Form } from 'formik'
import axios from 'axios'

const mockData = [
  {id: 1, content: "asdlkfjhalkjhaslkdjfh", timestamp: "lkjasdflkjh"},
  {id: 1, content: "asdlkfjhalkjhaslkdjfh", timestamp: "lkjasdflkjh"},
  {id: 1, content: "asdlkfjhalkjhaslkdjfh", timestamp: "lkjasdflkjh"},
  {id: 1, content: "asdlkfjhalkjhaslkdjfh", timestamp: "lkjasdflkjh"},
  {id: 1, content: "asdlkfjhalkjhaslkdjfh", timestamp: "lkjasdflkjh"},
]

function Feedback() {

  // suppose that the data is...

  const [feedback, setFeedback] = useState([]);
  const [currentFrequency, setCurrentFrequency] = useState("");

  useEffect(() => {
    getFeedbackFrequency()
    getFeedback()
  }, [])

  const handleSubmitNewFeedbackFrequency = (values) => {
    axios.get("/csrf", { withCredentials: true }).then((response) => {
        axios.post("/feedback-soliciation-frequency", {
            frequency: values.frequency
        }, {
            withCredentials: true,
            headers: {
                'X-CSRFToken': response.headers['x-csrftoken'],
                'Content-Type': 'multipart/form-data'
            }
        }).then((results) => {
            console.log(results)
            getFeedbackFrequency() // set the frequency to the updated value
        }).catch(err => {
            console.log(err)
        })
    })  
  }

  const getFeedbackFrequency = () => {
    axios.get("/feedback-soliciation-frequency"
        ).then((results) => {
            console.log(results)
            setCurrentFrequency(results.data.result)
        }).catch(err => {
            console.log(err)
        })
  }

  const getFeedback = () => {
    axios.get("/feedback"
        ).then((results) => {
            console.log(results)
            setFeedback(results.data.responses)
        }).catch(err => {
            console.log(err)
        })
  }

  function ordinal_suffix_of(i) {
    let j = i % 10,
        k = i % 100;
    if (j === 1 && k !== 11) {
        return i + "st";
    }
    if (j === 2 && k !== 12) {
        return i + "nd";
    }
    if (j === 3 && k !== 13) {
        return i + "rd";
    }
    return i + "th";
}

  return (
    <div className='px-8'>
      <span className="font-bold">Current feedback frequency</span>: {currentFrequency ? currentFrequency : "Not yet set"} <br/><br/>
      <Formik
        initialValues={{
            frequency: '',
        }}
        onSubmit={(values) => handleSubmitNewFeedbackFrequency(values)}>
        <Form>
            <div className='flex flex-row'>
                <div className='input-container'>
                    <label htmlFor="frequency">Change frequency: </label>
                    <Field id="frequency" name="frequency" placeholder={currentFrequency} className="stats-input" />
                </div>
            </div>

            <button type="submit" className='submit-button'>Set frequency</button>
        </Form>
      </Formik>

      Set feedback to 0 to never solicit feedback. 1 = after every meeting.

      <div className='flex flex-row flex-wrap'>
        {feedback.map((value, index) => (
          <div className='py-2 pr-2 last:pr-0 basis-1/5 text-white mt-4'>
            <div className='bg-slate-400 rounded-md w-full h-full p-4'>
              <div>
                Feedback: "
                {value.content}
                "
              </div>
              <div>
                Submitted by {value.user.first_name} {value.user.last_name} after their {ordinal_suffix_of(value.meetingNumber)} meeting.
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Feedback