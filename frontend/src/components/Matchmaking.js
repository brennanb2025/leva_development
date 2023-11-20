import { React, useEffect, useState } from 'react'
import Dropdown from 'react-dropdown'
import Modal from 'react-modal'
import axios from 'axios'

function Matchmaking() {

    const [modalProps, setModalProps] = useState({})
    const [modalOpen, setModalOpen] = useState(false)

    const [matches, setMatches] = useState({}) // All "confirmed" matches
    const [allUsers, setAllUsers] = useState([]) // All users
    const [mentees, setMentees] = useState([]) // All mentees
    const [feed, setFeed] = useState({})
    const [numMatches, setNumMatches] = useState({}) // Mapping from mentor to number of mentees pointing to mentor

    // Populate matches, mentees state
    useEffect(() => {
        const matchescall = axios.get("/admin-user-matches", {
            params: {
                "businessId": 1
            },
        })

        const userscall = axios.get("/admin-lookup-users-in-business", {
            params: {
                "businessId": 1
            },
        })

        Promise.all([matchescall, userscall]).then((results) => {
            let dict = {}
            results[0].data.map(m => {
                dict[m.user.id] = m.mentors
            })
            setMatches(dict)

            setAllUsers(results[1].data)
        })
    }, [])

    // As a consequence of the API call, the function should...
    // Update the matches state
    useEffect(() => {
        if (Object.keys(matches).length == 0) {
            return
        }
        let tempNum = numMatches
        Object.keys(matches).map((m) => {
            const mentors = matches[m]
            for (let i = 0; i < mentors.length; i++) {
                const m_id = mentors[i].id
                if (tempNum[m_id] === undefined) {
                    tempNum[m_id] = 1
                }
                else {
                    tempNum[m_id] += 1
                }
            }
            tempNum[m] = mentors.length
        })
        console.log(tempNum)
        setNumMatches(tempNum)
    }, [matches])

    // ...and update the mentees.
    useEffect(() => {
        // Perform filter here...
        if (allUsers.length == 0) {
            return
        }
        let filtered = allUsers.filter(m => m.is_mentee)
        let promises = []
        filtered.map((m) => {
            const feedcall = axios.get("/admin-lookup-user-feed-all", {
                params: {
                    "userid": m.id
                },
            })
            promises.push(feedcall)
        })

        Promise.all(promises).then((results) => {
            let temp = {}
            console.log(results)
            results.map((m) => {
                temp[m.data.userId] = m.data.matches
            })
            setFeed(temp)
        })
    }, [allUsers])

    useEffect(() => {
        let filtered = allUsers.filter(m => m.is_mentee)
        let grouped = Object.groupBy(filtered, (m) => matches[m.id] === undefined)
        if (Object.keys(grouped).length > 0) {
            filtered = grouped[false].concat(grouped[true])
        }
        setMentees(filtered)
    }, [feed])

    // "Helper functions"
    function MatchEntry(props) {

        let mentee = props.mentee
        let mentors = props.mentors
        let candidates = props.candidates.map(m => m.mentor)
        let index = props.index

        const [disabled, setDisabled] = useState(mentors !== undefined) //mentee in matches --> mentee was already matched
        const [selMentor, setSelMentor] = useState(null)

        if (candidates === undefined) {
            console.log("I hate this so much. die")
            return
        }

        let mentor
        if (mentors === undefined) {
            mentor = candidates[0]
        }
        else {
            mentor = mentors[0]
        }
        const options = candidates.map((m, i) => ({ label: m.first_name, value: i }))
        return (
            <div
                className={`w-full relative border p-3 mt-3 first:mt-0 flex flex-row justify-around items-center`}
                style={{ zIndex: (10 - index) * 10 }}>

                <div className="absolute w-full h-full bg-slate-100 hover:cursor-pointer"
                    onClick={() => {
                        setModalOpen(true)
                        setModalProps({ mentee: mentee, mentor: mentor })
                    }}></div>

                <div className='z-10 basis-1/3 flex flex-row justify-between items-center'
                    onClick={() => {
                        setModalOpen(true)
                        setModalProps({ mentee: mentee, mentor: mentor })
                    }}>
                    <div className="flex flex-row items-center basis-1/3">
                        <img className='pfp-image' src={mentee.profile_picture} alt=''></img>
                        {mentee.first_name}
                    </div>

                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>



                    <div className="flex flex-row items-center basis-1/3">
                        <img className='pfp-image' src={mentor.profile_picture} alt='' />
                        {mentor.first_name}
                    </div>
                </div>

                <div className='z-10 relative basis-1/3'>
                    <Dropdown
                        disabled={disabled}
                        options={options}
                        value={selMentor ? selMentor : { label: mentor.first_name, value: 0 }}
                        placeholder={"See alternative mentors..."}
                        className={disabled ? "bg-gray-500" : "bg-transparent"}
                        controlClassName="border"
                        menuClassName='absolute bg-slate-300 w-full'
                        onChange={(option) => {
                            setSelMentor(option)
                        }} />
                </div>

                <div className='z-10 basis-1/6'>
                    <button className="bg-green-400 p-2 w-full" onClick={async () => {
                        if (disabled == false) {
                            let m_id = candidates[selMentor.value].id
                            let numCopy = structuredClone(numMatches)
                            if (numCopy[m_id] === undefined) {
                                numCopy[m_id] = 1
                            }
                            else {
                                numCopy[m_id] = numCopy[m_id] + 1
                            }
                            numCopy[mentor.id] -= 1
                            if (numCopy[mentee.id] === undefined) {
                                numCopy[mentee.id] = 1
                            }
                            console.log(numCopy)
                            const query = await axios.get("/admin-validate-match", {
                                params: {
                                    mentorId: m_id,
                                    menteeId: mentee.id,
                                    numMatching: JSON.stringify(numCopy)
                                }
                            })
                            if (query.data.success) {
                                // change matching...
                                axios.get("/csrf", { withCredentials: true }).then((response) => {
                                    axios.post("/admin-apply-match", {
                                        menteeId: mentee.id,
                                        mentorId: m_id,
                                        numMatching: JSON.stringify(numCopy)
                                    }, {
                                        withCredentials: true,
                                        headers: {
                                            'X-CSRFToken': response.headers['x-csrftoken'],
                                            'Content-Type': 'multipart/form-data'
                                        }
                                    }).then((result) => { console.log(result) })
                                })
                                // Frontend changes...
                                setDisabled(!disabled)
                                setMatches(prev => {
                                    prev[mentee.id] = [candidates[selMentor.value]]
                                    return prev
                                })
                                setNumMatches(numCopy)
                            }
                            else {
                                console.log("invalid")
                            }
                        }
                        else {
                            setDisabled(!disabled)
                        }
                    }}>
                        {disabled ? "Edit" : "Confirm"}
                    </button>
                </div>
            </div>
        )
    }

    function EntryModal(props) {
        let mentor = props.mentor
        let mentee = props.user
        console.log(props)
        return (
            <Modal
                isOpen={modalOpen}
                onRequestClose={() => { setModalOpen(false) }}
                contentLabel="One small step for man, one giant leap for mankind"
                style={{ content: { zIndex: 20 } }}
            >
                <button onClick={() => { setModalOpen(false) }}>Close</button>

                <div className="w-full h-full flex flex-row">
                    {
                        [mentor, mentee].map((person) => (
                            <div className='flex-1 flex flex-col items-center'>
                                <img src={person.profile_picture} className="w-28 h-28 rounded-full" />
                                <div className='matchmaking-subheader mb-4'>{person.first_name} {person.last_name}</div>
                                <div className="text-start">
                                    {
                                        Object.keys(person).map((k, i) => {
                                            if (k === "profile_picture"
                                                || k === "first_name"
                                                || k === "last_name"
                                                || !person[k]) {
                                                return ""
                                            }
                                            else if (k === "resume") {
                                                return <a href={person[k]} className='text-blue-700 underline'>Resume</a>
                                            }
                                            else if (typeof person[k] == "object") {
                                                return (
                                                    <div>
                                                        <span className='font-bold'>{k}: </span>
                                                        <span>{
                                                            person[k].map((field, i) => {
                                                                if (i == person[k].length - 1) {
                                                                    return field
                                                                }
                                                                return field + ", "
                                                            })
                                                        }</span>
                                                    </div>
                                                )
                                            }

                                            return (
                                                <div>
                                                    <span className='font-bold'>{k}: </span>
                                                    <span>{person[k]}</span>
                                                </div>
                                            )
                                        })
                                    }
                                </div>
                            </div>
                        ))
                    }
                </div>
            </Modal>
        )
    }

    return (
        <div className="admin-parent-container">

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
                        mentees.map((m, i) => (<MatchEntry mentee={m} mentors={matches[m.id]} candidates={feed[m.id]} index={i} />))
                    }
                </div>

            </section>

            {Object.keys(modalProps).length != 0 ? <EntryModal user={modalProps.mentee} mentor={modalProps.mentor} /> : ""}

            <section className="w-full pt-8 flex justify-end py-8">
                <button className="bg-slate-400 p-4">
                    Confirm All
                </button>
            </section>
        </div>
    );
}

export default Matchmaking