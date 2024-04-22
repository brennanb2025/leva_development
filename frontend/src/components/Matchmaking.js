import { React, useEffect, useState } from 'react'
import axios from 'axios'
import "react-confirm-alert/src/react-confirm-alert.css"; // Import css
import MatchmakingScreen from './MatchmakingScreenAnimation';
import MatchEntry from './MatchEntry';
import EntryModal from './EntryModal';

function Matchmaking({ toggleMatchmakingScreenVisibility }) {

    const [modalProps, setModalProps] = useState({})
    const [modalOpen, setModalOpen] = useState(false)

    const [initialMatches, setInitialMatches] = useState({}) // All initial matches (when the screen loads), key: menteeid, value: mentorid
    const [matches, setMatches] = useState({}) // All "confirmed" matches, key: menteeid, value: mentorid
    const [allUsers, setAllUsers] = useState([]) // All users
    const [mentees, setMentees] = useState({true: [], false: []}) // All mentees
    const [feed, setFeed] = useState({})
    const [numMatches, setNumMatches] = useState({}) // Mapping from mentor to number of mentees pointing to mentor

    // Populate matches, mentees state
    useEffect(() => {
        const matchescall = axios.get("/admin-user-matches")

        const userscall = axios.get("/admin-lookup-users-in-business")

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
    // TODO: Make this call faster, because it seems to be getting blocked pretty hard here
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
                const sortedMatches = m.data.matches.sort(sortMatches)
                temp[m.data.userId] = sortedMatches
            })
            console.log("matches:",temp)
            setFeed(temp)
        })
    }, [allUsers])

    function sortMatches(m1, m2) {
        return m2.score - m1.score
    }

    useEffect(() => {
        let filtered = allUsers.filter(m => m.is_mentee)
        let grouped = Object.groupBy(filtered, (m) => matches[m.id] === undefined)
        if(grouped[false] === undefined){
            grouped[false] = []
        }
        if(grouped[true] === undefined){
            grouped[true] = []
        }
        setMentees(grouped)
    }, [feed])

    // ...or update matches here.
    function submitMatches() {

        toggleMatchmakingScreenVisibility(true);

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

                <div className="overflow-y-scroll flex-1 z-0 mt-4 flex flex-col items-center">
                    {
                        mentees[true] ? mentees[true].map((m, i) => (
                            <MatchEntry mentee={m} mentors={matches[m.id]} candidates={feed[m.id]} index={i} 
                                setModalProps={setModalProps} setModalOpen={setModalOpen}
                                matches={matches} setMatches={setMatches} numMatches={numMatches} setNumMatches={setNumMatches}
                                allUsers={allUsers} setMentees={setMentees}
                            />
                        )) : ""
                    }
                    {
                        mentees[false] ? mentees[false].map((m, i) => (
                            <MatchEntry mentee={m} mentors={matches[m.id]} candidates={feed[m.id]} index={mentees[true].length + i} 
                                setModalProps={setModalProps} setModalOpen={setModalOpen}
                                matches={matches} setMatches={setMatches} numMatches={numMatches} setNumMatches={setNumMatches}
                                allUsers={allUsers} setMentees={setMentees}
                            />
                        )) : ""
                    }
                </div>

            </section>

            {Object.keys(modalProps).length != 0 ? 
            <EntryModal user={modalProps.mentee} mentor={modalProps.mentor} 
                setModalOpen={setModalOpen} modalOpen={modalOpen} feed={feed}
            /> 
            : ""}

            <section className="w-full pt-8 flex justify-end py-8">
                <button className="bg-slate-400 p-4" onClick={submitMatches}>
                    Submit all matches
                </button>
            </section>
        </div>
    );
}

export default Matchmaking