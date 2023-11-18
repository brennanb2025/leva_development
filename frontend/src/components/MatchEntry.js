import React from 'react'
import Dropdown from 'react-dropdown'
import axios from 'axios'
import { useState } from 'react'

function MatchEntry(props) {

    // let mentors = matches[mentee.id]
    // let mentor

    const [disabled, setDisabled] = useState(mentors !== undefined)
    const [selMentor, setSelMentor] = useState(null)

    // let candidates = feedMatches[mentee.id]
    //     .sort((x, y) => y.score - x.score)
    //     .map(m => ({ label: m.mentor.first_name, value: m.mentor.id }))

    let index = props.index
    let candidates = props.candidates
    let mentors = props.mentors
    let mentee = props.mentee

    if (feedMatches[mentee.id] === undefined) {
        return ""
    }
    if (mentors === undefined) {
        mentor = feedMatches[mentee.id][0].mentor
    }
    else {
        mentor = matches[mentee.id][0]
    }


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
                    <img className='pfp-image' src={mentor.profile_picture} alt='' />
                    {mentor.first_name}
                </div>
            </div>

            <div className='z-10 relative basis-1/3'>
                <Dropdown
                    disabled={disabled}
                    options={candidates}
                    value={selMentor ? selMentor : candidates[0]}
                    placeholder={"See alternative mentors..."}
                    className={disabled ? "bg-gray-500" : "bg-transparent"}
                    controlClassName="border"
                    menuClassName='absolute bg-slate-300 w-full'
                    onChange={(option) => {
                        console.log(option)
                        setSelMentor(option)
                    }} />
            </div>

            <div className='z-10 basis-1/6'>
                <button className="bg-green-400 p-2 w-full" onClick={() => {
                    if (disabled == false) {
                        // axios api call to check?
                        axios.get("/admin-validate-match", {
                            params: {
                                mentorId: selMentor.value,
                                menteeId: mentee.id,
                                numMatching: JSON.stringify(numMatches)
                            },
                        }).then((results) => {
                            console.log(results)
                            if (!results.data.success) {
                                return
                            }
                            // If api returns correct, then apply change to 
                            axios.get("/csrf", { withCredentials: true }).then((response) => {
                                axios.post("/admin-apply-match", {
                                    mentorId: selMentor.value,
                                    menteeId: mentee.id
                                }, {
                                    withCredentials: true,
                                    headers: {
                                        'X-CSRFToken': response.headers['x-csrftoken'],
                                        'Content-Type': 'multipart/form-data'
                                    }
                                }).then((results) => {
                                    console.log(results)
                                    let newdict = matches
                                    newdict[mentee.id] = selMentor
                                    numMatches[selMentor.value] += 1
                                    setMatches(newdict)
                                }).catch(err => {
                                    console.log(err)
                                })
                            })
                        })
                    }
                    setDisabled(!disabled)
                }}>
                    {disabled ? "Edit" : "Confirm"}
                </button>
            </div>
        </div>
    )
}

export default MatchEntry