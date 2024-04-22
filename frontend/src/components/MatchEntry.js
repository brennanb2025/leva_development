import {React, useState} from 'react'
import Dropdown from 'react-dropdown'
import { confirmAlert } from "react-confirm-alert"; // Import
import axios from 'axios'

function MatchEntry({matches, setMatches, allUsers, setMentees, numMatches, setNumMatches, setModalOpen, setModalProps, ...props}) {

  let mentee = props.mentee
  let mentors = props.mentors
  let candidates = props.candidates.map(m => m.mentor)
  let index = props.index

  const [disabled, setDisabled] = useState(mentors !== undefined) //mentee in matches --> mentee was already matched
  const [selMentor, setSelMentor] = useState({ label: mentor ? mentor.first_name : "Select mentor...", value: mentors === undefined ? 0 : -1 })
  const [updateStatus, setUpdateStatus] = useState(1)

  let mentor
  if (mentors !== undefined) {
      mentor = mentors[0]
      candidates = candidates.filter(m => m.id !== mentor.id)
  }

  const options = candidates.map((m, i) => ({ label: m.first_name, value: i }))
  let color = !disabled ? "bg-purple-200" : "bg-slate-100"

    // "Helper functions"
    const validateMatch = async (mentee, mentor, numMatchings) => {
        console.log(mentee.id, mentor.id, numMatchings)
        const query = await axios.get("/admin-validate-match", {
            params: {
                menteeId: mentee.id,
                mentorId: mentor.id,
                numMatching: JSON.stringify(numMatchings)
            }
        })
        return query.data
    }

    const resolveConflict = (mentee, currMentor, candidate, tempNum) => {
        confirmAlert({
            title: "Resolve conflict",
            message: "There is a conflict between the current mentor and the candidate. Do you want to resolve it?",
            buttons: [
                {
                    label: "Yes",
                    onClick: () => {
                        // API call to resolve conflict
                        console.log("Resolving conflict", mentee, currMentor, candidate)
                        updateState(mentee, currMentor, candidate, tempNum)
                    }
                },
                {
                    label: "No",
                    onClick: () => {
                        // Do nothing
                    }
                }
            ]
        })
    }

  const updateState = (mentee, currMentor, candidate, numMatches, displacedMentee = undefined) => {
    let temp = { ...numMatches }
    if (currMentor) {
        temp[currMentor.id] -= 1
    }
    temp[candidate.id] += 1
    temp[mentee.id] = 1
    if (displacedMentee) {
        temp[displacedMentee.id] -= 1
    }
    console.log("new numMatches", temp)
    setNumMatches(temp)
    setDisabled(true)
  }

  const checkMatch = async () => {
    if(disabled) {
        setDisabled(false)
        return
    }

    // Need to check if selection is viable
    if(selMentor.value === -1) {
        return;
    }

    // Current candidate:
    const candidate = candidates[selMentor.value]

    // Take copy of numMatches ane edit to represent the selection
    let tempNum = numMatches
    // current mentee (always 0 probably, to represent vacancy)
    tempNum[mentee.id] = 0
    // Mentor to be added, show that matching wants to happen
    if(!tempNum[candidate.id]){
        tempNum[candidate.id] = 0
    }
    // If there was a mentor before, remove
    if(mentor){
        if(tempNum[mentor.id] === 1){
            delete tempNum[mentor.id]
        }
        else{
            tempNum[mentor.id] -= 1
        }
    }

    // Run the API call to check the matches (probably a helper)
    validateMatch(mentee, candidate, tempNum).then((res) => {
        console.log(res)
        
        // If the match is viable, update the state
        if(res.success){
            updateState(mentee, mentor, tempNum, candidate)
        }
        // else, alert the user that the match is not viable
        else{
            resolveConflict(mentee, mentor, candidate, tempNum)
        }
    })
  }

  return (
      <div
          className={`w-full relative p-3 mt-4 first:mt-0 flex flex-row justify-around items-center`}
          style={{ zIndex: (10 - index) * 10 }}>

          <div className='z-10 basis-1/3 flex flex-row justify-between items-center peer'
              onClick={() => {
                  setModalOpen(true)
                  setModalProps({ mentee: mentee, mentor: mentor ? mentor : selMentor.label === "Select mentor..." ? undefined : candidates[selMentor.value] })
                  // show selected mentor if the user has selected one
              }}>
              <div className="flex flex-row items-center basis-1/3 font-bold">
                  {mentee.profile_picture === null ?
                      <img className='pfp-image' src={process.env.PUBLIC_URL + "/blank-profile-picture.png"} alt=''></img>
                      : <img className='pfp-image' src={mentee.profile_picture} alt=''></img>
                  }

                  {mentee.first_name}
              </div>

              <div className='font-bold text-xl'>
                  &
              </div>

              <div className="flex flex-row items-center basis-1/3 font-bold">
                  {mentor &&
                      (mentor.profile_picture === null ?
                          <img className='pfp-image' src={process.env.PUBLIC_URL + "/blank-profile-picture.png"} alt=''></img>
                          : <img className='pfp-image' src={mentor.profile_picture} alt='' />)
                  }
                  {mentor ? mentor.first_name : ""}
              </div>
          </div>

          <div className='flex flex-row z-10 relative basis-1/3 peer'>
              <Dropdown
                  disabled={disabled}
                  options={options}
                  value={selMentor}
                  placeholder={"See alternative mentors..."}
                  arrowClosed={<span>
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" data-slot="icon" class="w-6 h-6">
                          <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                      </svg>
                  </span>}
                  arrowOpen={<span>
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" data-slot="icon" class="w-6 h-6">
                          <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
                      </svg>
                  </span>}
                  className={disabled ? "bg-white cursor-not-allowed flex-1 flex-grow" : "bg-white cursor-pointer flex-1 flex-grow"}
                  controlClassName="border flex flex-row justify-between"
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

          <div className='z-10 basis-1/6 peer'>
              <button className="bg-secondary p-2 w-full text-white" onClick={checkMatch}>
                  {disabled ? "Edit" : "Confirm"}
              </button>
          </div>

          <div className={"absolute w-full h-full hover:cursor-pointer border scale-[0.98] hover:scale-100 peer-hover:scale-100 duration-200 " + color}
              onClick={() => {
                  setModalOpen(true)
                  setModalProps({ mentee: mentee, mentor: mentor })
              }}></div>
      </div>
  )
}

export default MatchEntry