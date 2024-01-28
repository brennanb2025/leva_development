import React, { useState } from 'react'

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

  return (
    <div>
      {feedback.map((value, index) => (
        <div>
          {JSON.stringify(value)}
        </div>
      ))}
    </div>
  )
}

export default Feedback