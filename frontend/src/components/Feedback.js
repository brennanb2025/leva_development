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

  const [feedback, setFeedback] = useState(mockData);
  const [currentFrequency, setCurrentFrequency] = useState("");

  useEffect(() => {
    getFeedbackFrequency()
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

  return (
    <div className='px-8'>
      <span className="font-bold">Current frequency</span>: {currentFrequency ? currentFrequency : "Not yet set"} <br/><br/>
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
                Submitted at time: {value.timestamp}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Feedback