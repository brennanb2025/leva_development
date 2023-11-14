import { React, useState, useEffect } from 'react'
import Dropdown from 'react-dropdown'
import Modal from 'react-modal'
import axios from 'axios'

function Matchmaking() {

    const [selected, setSelected] = useState(-1)
    const [modalOpen, setModalOpen] = useState(false)
    const [matches, setMatches] = useState([])
    //matches = [{mentee id : [mentor user objects]}]

    //const [allUsers, setAllUsers] = useState([])
    const [allMentees, setAllMentees] = useState([])
    //allMentees = [user]
    const [feedMatches, setFeedMatches] = useState({})

    useEffect(() => {

        axios.get("/admin-user-matches", {
            params: {
                "businessId": 1
            },
        }).then((results) => {
            const newDict = {}
            results.data.map((element) => {
                newDict[element["user"].id] = element["mentors"].map(m => m.id) //set user id : [ mentor id ]
            })

            setMatches(newDict)

        })

        axios.get("/admin-lookup-users-in-business", {
            params: {
                "businessId": 1
            },
        }).then((results) => {
            console.log(results.data)
            //setAllUsers(results.data)

            let feed = {}
            results.data.filter(m => m.is_mentee).map((m) => {
                axios.get("/admin-lookup-user-feed-all", {
                    params: {
                        "userid": m.id
                    },
                }).then((results) => {
                    //setAllUsers(results.data)
                    feed[m.id] = results.data.matches
                })
            })
            setFeedMatches(feed)
            setAllMentees(results.data.filter(m => m.is_mentee))
        })
    }, [])
    // useEffect(() => {
    //     allMentees.map((m) => {
    //         axios.get("/admin-lookup-user-feed-all", {
    //             params: {
    //                 "userid": m.id
    //             },
    //         }).then((results) => {
    //             //setAllUsers(results.data)
    //             feed[m] = results.data.matches
    //         })
    //     })
    //     setFeedMatches(feed)
    // }, [allMentees])

    // "Helper functions"
    function MatchEntry(props) {

        /*let matchdata = props.match
        let mentee = matchdata.user;
        let mentor = matchdata.mentors[0]*/

        //let matchData = 
        let mentee = props.mentee
        let mentors = matches[mentee.id] //get the match from the matches obj (stores mentee id : mentor id)

        console.log("allMentees", allMentees)
        //console.log("mentors == undefined", mentors === undefined)

        const [disabled, setDisabled] = useState(mentors === undefined) //mentee in matches --> mentee was already matched

        if (mentors === undefined) {
            console.log("mentee", mentee, "was not matched yet")
            //setDisabled(false)
            return
        }

        console.log("mentors:", mentors)
        console.log("mentee ", mentee)
        console.log("mentee id,", mentee.id)
        console.log("feedMatches ", feedMatches)
        console.log("feedMatches ", feedMatches[mentee.id])
        let candidates = feedMatches[mentee.id].map(m => m.mentor.first_name)
        console.log(candidates)
        /*for (let i = 0; i < matchdata.mentors.length; i++) {
            let mentorinfo = matchdata.mentors[i]
            candidates.push(mentorinfo.first_name)
        }*/
        let index = props.index

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
                        <img className='pfp-image' src={mentee.profile_picture} alt=''></img>
                        {mentee.first_name}
                    </div>

                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>



                    <div className="flex flex-row items-center basis-1/3">
                        <img className='pfp-image' src={mentors[0].profile_picture} alt='' />
                        {mentors[0].first_name}
                    </div>
                </div>

                <div className='z-10 relative basis-1/3'>
                    <Dropdown
                        disabled={disabled}
                        options={candidates}
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

    function EntryModal() {
        let mentor = matches[selected].mentors[0]
        let mentee = matches[selected].user
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
                                            console.log(typeof person[k])
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
                        allMentees.map((m, i) => <MatchEntry mentee={m} index={i} />)
                    }
                </div>

            </section>

            {selected != -1 ? <EntryModal /> : ""}

            <section className="w-full pt-8 flex justify-end py-8">
                <button className="bg-slate-400 p-4">
                    Confirm All
                </button>
            </section>
        </div>
    );
}

export default Matchmaking