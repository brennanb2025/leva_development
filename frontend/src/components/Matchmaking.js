import { React, useEffect, useState } from 'react'
import Dropdown from 'react-dropdown'
import Modal from 'react-modal'
import axios from 'axios'
import { confirmAlert } from "react-confirm-alert"; // Import
import "react-confirm-alert/src/react-confirm-alert.css"; // Import css

function Matchmaking() {

    const [modalProps, setModalProps] = useState({})
    const [modalOpen, setModalOpen] = useState(false)

    const [initialMatches, setInitialMatches] = useState({}) // All initial matches (when the screen loads), key: menteeid, value: mentorid
    const [matches, setMatches] = useState({}) // All "confirmed" matches, key: menteeid, value: mentorid
    const [allUsers, setAllUsers] = useState([]) // All users
    const [mentees, setMentees] = useState([]) // All mentees
    const [feed, setFeed] = useState({})
    const [numMatches, setNumMatches] = useState({}) // Mapping from mentor to number of mentees pointing to mentor

    const [replacedUsers, setReplacedUsers] = useState([])

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
            setInitialMatches(dict)

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
            console.log(temp)
            setFeed(temp)
        })
    }, [allUsers])

    useEffect(() => {
        let filtered = allUsers.filter(m => m.is_mentee)
        let grouped = Object.groupBy(filtered, (m) => matches[m.id] === undefined)
        setMentees(grouped)
    }, [feed])

    // "Helper functions"
    function MatchEntry(props) {

        let mentee = props.mentee
        let mentors = props.mentors
        let candidates = props.candidates.map(m => m.mentor)
        let index = props.index

        let mentor
        if (mentors !== undefined) {
            mentor = mentors[0]
        }

        const [disabled, setDisabled] = useState(mentors !== undefined) //mentee in matches --> mentee was already matched
        const [selMentor, setSelMentor] = useState({ label: mentor ? mentor.first_name : "Select mentor...", value: mentors === undefined ? 0 : -1 })
        const [updateStatus, setUpdateStatus] = useState(1)

        const options = candidates.map((m, i) => ({ label: m.first_name, value: i }))
        let color = !disabled ? "bg-purple-200" : "bg-slate-100"
        return (
            <div
                className={`w-full relative border p-3 mt-3 first:mt-0 flex flex-row justify-around items-center`}
                style={{ zIndex: (10 - index) * 10 }}>

                <div className={"absolute w-full h-full hover:cursor-pointer " + color}
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
                        {mentee.profile_picture === null ?
                            <img className='pfp-image' src="/blank-profile-picture.png" alt=''></img>
                            : <img className='pfp-image' src={mentee.profile_picture} alt=''></img>
                        }

                        {mentee.first_name}
                    </div>

                    <div className='font-bold text-xl'>
                        &
                    </div>

                    <div className="flex flex-row items-center basis-1/3">
                        {mentor &&
                            (mentee.profile_picture === null ?
                                <img className='pfp-image' src="/blank-profile-picture.png" alt=''></img>
                                : <img className='pfp-image' src={mentor.profile_picture} alt='' />)
                        }
                        {mentor ? mentor.first_name : ""}
                    </div>
                </div>

                <div className='flex flex-row z-10 relative basis-1/3'>
                    <Dropdown
                        disabled={disabled}
                        options={options}
                        value={selMentor}
                        placeholder={"See alternative mentors..."}
                        className={disabled ? "bg-white cursor-not-allowed flex-1 flex-grow" : "bg-white cursor-pointer flex-1 flex-grow"}
                        controlClassName="border"
                        menuClassName='absolute bg-slate-300 w-full z-[100]'
                        onChange={(option) => {
                            setSelMentor(option)
                        }} />

                    {
                        updateStatus == 0 &&
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 text-red-500">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>

                    }
                    {
                        updateStatus == 2 &&
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 text-green-500">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>

                    }
                </div>

                <div className='z-10 basis-1/6'>
                    <button className="bg-green-400 p-2 w-full" onClick={async () => {
                        if (disabled == false) {

                            if (mentors && (selMentor.value == -1 || candidates[selMentor.value].id == mentor.id)) {
                                setDisabled(!disabled)
                                return
                            }

                            let m_id = candidates[selMentor.value].id
                            let numCopy = structuredClone(numMatches)
                            // Changes start here
                            if (numCopy[m_id] === undefined) {
                                numCopy[m_id] = 1
                            }
                            else {
                                numCopy[m_id] += 1
                            }

                            if (mentor) {
                                numCopy[mentor.id] -= 1
                            }

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
                                // Frontend changes...
                                setDisabled(!disabled)
                                setUpdateStatus(2)
                                setTimeout(() => setUpdateStatus(1), "3000")
                                setMatches(prev => {
                                    prev[mentee.id] = [candidates[selMentor.value]]
                                    return prev
                                })
                                /*if(initialMatches[menteeId] === candidates[selMentor.value]) {
                                    if()
                                    const copyReplacedUsers = {...replacedUsers}
                                    delete copyReplacedUsers[menteeId]
                                } 
                                else {
                                    setReplacedUsers(...replacedusers, menteeId)
                                    //if different than the initial match, set the 
                                }*/
                                setNumMatches(numCopy)
                                if (!mentors) {
                                    setMentees(prev => {
                                        prev[false].push(mentee)
                                        prev[true].splice(prev[true].indexOf(mentee), 1)
                                        return prev
                                    })
                                }
                            }
                            else {
                                console.log("invalid")
                                setUpdateStatus(0)
                                setTimeout(() => setUpdateStatus(1), "3000")

                                let conflicts = []
                                console.log(conflicts)
                                // Find the conflicts...
                                for (const [key, value] of Object.entries(matches)) {
                                    if (value[0].id == candidates[selMentor.value].id) {
                                        console.log(parseInt(key))
                                        conflicts.push(parseInt(key))
                                    }
                                }
                                // modal here...
                                confirmAlert({
                                    title: "Confirm to reorder",
                                    message: "This mentor is current matched with these other mentees. Select one to mentee to replace...",
                                    buttons: conflicts.map((menteeid) => {
                                        const conflictMentee = allUsers.find(obj => {
                                            return obj.id === menteeid
                                        })
                                        return ({
                                            label: conflictMentee.first_name,
                                            onClick: () => {
                                                setMentees(prev => {
                                                    if (!mentors) {
                                                        prev[false].push(mentee)
                                                        prev[true].splice(prev[true].indexOf(mentee), 1)
                                                    }
                                                    prev[true].push(conflictMentee)
                                                    prev[false].splice(prev[false].indexOf(conflictMentee), 1)
                                                    return prev
                                                })
                                                let numCopy = structuredClone(numMatches)

                                                if (numCopy[mentee.id] === undefined) {
                                                    numCopy[mentee.id] = 1
                                                }
                                                else {
                                                    numCopy[mentee.id] += 1
                                                }
                                                numCopy[conflictMentee.id] -= 1

                                                setNumMatches(numCopy)
                                                setMatches(prev => {
                                                    prev[mentee.id] = [candidates[selMentor.value]]
                                                    delete prev[conflictMentee.id]
                                                    return prev
                                                })
                                            }
                                        })
                                    }).concat([{ label: "Cancel", onClick: () => { "" } }])
                                });
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

        let displayinfo = [mentee]
        if (mentor !== undefined) {
            displayinfo.push(mentor)
        }

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
                        displayinfo.map((person) => (
                            <div className='flex-1 flex flex-col items-center'>
                                <img src={person.profile_picture} className="w-28 h-28 rounded-full" />
                                <div className='matchmaking-subheader mb-4'>{person.first_name} {person.last_name}</div>
                                <div>
                                    <span className='font-bold'>{person.is_mentee ? "Mentee" : "Mentor"}</span>
                                </div>
                                <div>
                                    <span className='font-bold'>Email: </span> 
                                    <span>{person.email}</span>
                                </div>
                                <div>
                                    <span className='font-bold'>Bio: </span> 
                                    <span>{person.bio}</span>
                                </div>
                                {/* <div>
                                    <span className='font-bold'>Division: </span> 
                                    <span>{person.division}</span>
                                </div>
                                <div>
                                    <span className='font-bold'>Division preference: </span> 
                                    <span>{person.division_preference}</span>
                                </div>
                                <div>
                                    <span className='font-bold'>Current occupation: </span> 
                                    <span>{person.current_occupation}</span>
                                </div> */}
                                <div>
                                    <span className='font-bold'>Personality traits: </span> 
                                    <span>{person.personality_1}, {person.personality_2}, {person.personality_3}</span>
                                </div>

                                {
                                    person.is_mentee ?
                                        <div>
                                            <span className='font-bold'>Mentor gender preference: </span> 
                                            <span>{person.mentor_gender_preference}</span>
                                        </div>
                                        :
                                        <div>
                                            <span className='font-bold'>Gender identity: </span> 
                                            <span>{person.gender_identity}</span>
                                        </div>
                                }

                                <div>
                                    <span className='font-bold'>{person.is_mentee ? "Career interests: " : "Career experience: "}</span>
                                    <span>{
                                        person.career_interests.map((field, i) => {
                                            if (i == person.career_interests.length - 1) {
                                                return field
                                            }
                                            return field + ", "
                                        })
                                    }</span>
                                </div>
                                <div>
                                    <span className='font-bold'>Interests: </span>
                                    <span>{
                                        person.interests.map((field, i) => {
                                            if (i == person.interests.length - 1) {
                                                return field
                                            }
                                            return field + ", "
                                        })
                                    }</span>
                                </div>
                                <div>
                                    <span className='font-bold'>Education: </span>
                                    <span>{
                                        person.education.map((field, i) => {
                                            if (i == person.education.length - 1) {
                                                return field
                                            }
                                            return field + ", "
                                        })
                                    }</span>
                                </div>

                                {
                                    !person.is_mentee &&
                                    <span className='font-bold'>
                                        Can make {person.num_pairings_can_make === null || person.num_pairings_can_make === 1 ? "1 match" : person.num_pairings_can_make + " matches"}
                                    </span> 
                                }

                                <a href={person.resume} target="_blank" className='text-blue-700 underline'>Resume</a>

                                
                                {/* <div className="text-start">
                                    <a href={person.resume} className='text-blue-700 underline'>Resume</a>
                                    {
                                        // string.charAt(0).toUpperCase() + string.slice(1);
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
                                                let klabel = k.charAt(0).toUpperCase() + k.slice(1)
                                                klabel = klabel.replace(/_/g, " ")
                                                return (
                                                    <div>
                                                        <span className='font-bold'>{klabel}: </span>
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
                                            k = k.charAt(0).toUpperCase() + k.slice(1)
                                            return (
                                                <div>
                                                    <span className='font-bold'>{k.replace(/_/g, " ")}: </span>
                                                    <span>{person[k]}</span>
                                                </div>
                                            )
                                        })
                                    }
                                </div> */}
                            </div>
                        ))
                    }
                </div>
            </Modal>
        )
    }

    function submitMatches() {

        let l = structuredClone(matches)

        Object.keys(l).forEach(function (key, index) {
            l[key] = l[key][0].id;
        });

        console.log(l)

        axios.get("/csrf", { withCredentials: true }).then((response) => {
            //axios.post("/admin-apply-matches", {
            axios.post("/admin-apply-matches-if-unmatched", {
                matches: JSON.stringify(l)
            }, {
                withCredentials: true,
                headers: {
                    'X-CSRFToken': response.headers['x-csrftoken'],
                    'Content-Type': 'multipart/form-data'
                }
            }).then((results) => {
                console.log(results)
            }).catch(err => {
                console.log(err)
            })
        })
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
                        mentees[true] ? mentees[true].map((m, i) => (<MatchEntry mentee={m} mentors={matches[m.id]} candidates={feed[m.id]} index={i} />)) : ""
                    }
                    {
                        mentees[false] ? mentees[false].map((m, i) => (<MatchEntry mentee={m} mentors={matches[m.id]} candidates={feed[m.id]} index={mentees[true].length + i} />)) : ""
                    }
                </div>

            </section>

            {Object.keys(modalProps).length != 0 ? <EntryModal user={modalProps.mentee} mentor={modalProps.mentor} /> : ""}

            <section className="w-full pt-8 flex justify-end py-8">
                <button className="bg-slate-400 p-4" onClick={submitMatches}>
                    Submit all matches
                </button>
            </section>
        </div>
    );
}

export default Matchmaking