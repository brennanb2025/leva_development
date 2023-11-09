import { React, useState, useEffect } from 'react'
import Dropdown from 'react-dropdown'
import Modal from 'react-modal'
import axios from 'axios'
import MENTEE from '../static/nulogo.png'
import MENTOR from '../static/nulogo.png'

function Matchmaking() {

    const [selected, setSelected] = useState(-1)
    const [modalOpen, setModalOpen] = useState(false)

    let mockData = []

    for (let i = 0; i < 10; i++) {
        mockData.push(
            {
                mentee: "menteeName" + i,
                mentor: "mentorName" + i,
                menteeImage: MENTEE,
                mentorImage: MENTOR,
                candidates: [
                    "mentorName" + i,
                    "hi" + i,
                    "hi",
                    "hi",
                    "hi",
                    "hi"
                ]
            }
        )
    }

    useEffect(() => {
        axios.get("/admin-user-matches?businessId=1").then((res) => {
            console.log(res.data)
        }).catch((err) => {
            console.log(err)
        })
    }, [])

    function MatchEntry(props) {

        let matchdata = props.match
        let index = props.index

        const [disabled, setDisabled] = useState(false)

        return (
            <div
                className={`w-full relative border p-3 mt-3 first:mt-0 flex flex-row justify-around items-center`}
                style={{ zIndex: (10 - index) * 10 }}>

                <div className="absolute w-full h-full bg-slate-100 hover:cursor-pointer"
                    onClick={() => {
                        setModalOpen(true)
                        setSelected(index)
                    }}></div>

                <div className='z-10 basis-1/3 flex flex-row justify-between items-center'
                    onClick={() => {
                        setModalOpen(true)
                        setSelected(index)
                    }}>
                    <div className="flex flex-row items-center basis-1/3">
                        <img className='pfp-image' src={matchdata.menteeImage} alt=''></img>
                        {matchdata.mentee}
                    </div>

                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>



                    <div className="flex flex-row items-center basis-1/3">
                        <img className='pfp-image' src={matchdata.mentorImage} alt='' />
                        {matchdata.mentor}
                    </div>
                </div>

                <div className='z-10 relative basis-1/3'>
                    <Dropdown
                        disabled={disabled}
                        options={matchdata.candidates}
                        placeholder={"See alternative mentors..."}
                        className={disabled ? "bg-gray-500" : "bg-transparent"}
                        controlClassName="border"
                        menuClassName='absolute bg-slate-300 w-full' />
                </div>

                <div className='z-10 basis-1/6'>
                    <button className="bg-green-400 p-2 w-full" onClick={() => { setDisabled(!disabled) }}>
                        {disabled ? "Edit" : "Confirm"}
                    </button>
                </div>
            </div>
        )
    }


    return (
        <div className="h-full w-full px-8 flex flex-col">

            <section className='w-full p-3 flex flex-row justify-around border-b mb-2'>

                <div className='entry-label basis-1/3 flex flex-row justify-between'>

                    <div className='basis-1/3 text-center'>
                        Mentee
                    </div>

                    <div className='basis-1/3 text-center'>
                        Mentor
                    </div>

                </div>
                <div className='entry-label basis-1/3'>Alternatives</div>
                <div className='entry-label basis-1/6'>Confirm</div>

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
                <button onClick={() => { setModalOpen(false) }}>Close</button>

                {selected != -1 ?
                    (
                        <div className="w-full flex flex-row">
                            <div className='flex-1 flex flex-col items-center'>
                                <img src={mockData[selected].menteeImage} className="w-28 h-28 rounded-full" />
                                <div className="matchmaking-header mt-2 border-b px-4 pb-2">{mockData[selected].mentee}</div>
                            </div>
                            <div className='flex-1 flex flex-col items-center'>
                                <img src={mockData[selected].menteeImage} className="w-28 h-28 rounded-full" />
                                <div className="matchmaking-header mt-2 border-b px-4 pb-2">{mockData[selected].mentor}</div>
                            </div>
                        </div>
                    )
                    : ""
                }
            </Modal>

            <section className="w-full pt-8 flex justify-end py-8">
                <button className="bg-slate-400 p-4">
                    Confirm All
                </button>
            </section>
        </div>
    );
}

export default Matchmaking