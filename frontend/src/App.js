import logo from './logo.svg';
import './App.css';
import axios from 'axios'
import { useState, useEffect, memo } from 'react'
import Dropdown from 'react-dropdown'
import Modal from 'react-modal';

function App() {

  const [events, setEvents] = useState()
  const [selected, setSelected] = useState(-1)
  const [modalOpen, setModalOpen] = useState(false)

  const mockMatch = {
    mentee: "sup",
    mentor: "maybe",
    candidates: [
      "hi",
      "hi",
      "hi",
      "hi",
      "hi"
    ]
  }

  let mockData = []

  for (let i = 0; i < 10; i++) {
    mockData.push(mockMatch)
  }

  useEffect(() => {
    axios.get("/test-endpoint").then((res) => {
      console.log(res)
    }).catch((err) => {
      console.log(err)
    })
  }, [])

  function MatchEntry(props) {

    let matchdata = props.match

    return (
      <div
        className={`w-full relative border p-3 mt-3 first:mt-0 flex flex-row justify-around items-center`}
        style={{ zIndex: (10 - props.index) * 10 }}>

        <div className="absolute w-full h-full bg-slate-100 hover:cursor-pointer"
          onClick={() => setModalOpen(true)}></div>
        <div className="z-10">{matchdata.mentee}</div>

        <div className="z-10"> {matchdata.mentor}</div>

        <div className='z-10 relative w-1/3'>
          <Dropdown
            options={matchdata.candidates}
            placeholder={"Alternatives..."}
            controlClassName="border"
            menuClassName='absolute bg-slate-300 w-full' />
        </div>

        <button className="bg-green-400 p-2 z-10">Lock</button>
      </div>
    )
  }


  return (
    <div className="h-screen w-screen p-8 flex flex-col">
      <section className="w-full py-8">
        <div className="matchmaking-header border-b pb-2">Matchmaking</div>
      </section>

      <section className="flex-grow overflow-y-hidden flex flex-row">

        <div className="overflow-y-scroll flex-1 z-0">
          {
            mockData.map((data, index) => <MatchEntry match={data} index={index} />)
          }
        </div>

      </section>

      <Modal
        isOpen={modalOpen}
        onRequestClose={() => { setModalOpen(false) }}
        contentLabel="One small step for man, one giant leap for mankind"
        style={{ content: { zIndex: 20 } }}
      >
        <div>
          Despite everything, it's still you.
        </div>
        <button onClick={() => { setModalOpen(false) }}>Close</button>
      </Modal>

      <section className="w-full pt-8 flex justify-end p-8">
        <button className="bg-slate-400 p-4">
          Confirm All
        </button>
      </section>
    </div>
  );
}

export default App;
