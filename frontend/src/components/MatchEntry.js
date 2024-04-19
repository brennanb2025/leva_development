import {React, useState} from 'react'
import Dropdown from 'react-dropdown'
import { confirmAlert } from "react-confirm-alert"; // Import
import axios from 'axios'

// "Helper functions"
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
  }

  const options = candidates.map((m, i) => ({ label: m.first_name, value: i }))
  let color = !disabled ? "bg-purple-200" : "bg-slate-100"

  // Potentially update match here?
  const checkMatch = async () => {
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
                  console.log("prev:", prev)
                  prev[mentee.id] = [candidates[selMentor.value]]
                  console.log("new:", prev)
                  return prev
              })
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
              console.log(matches)
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