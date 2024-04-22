import {React} from 'react'
import Modal from 'react-modal'


function EntryModal({setModalOpen, modalOpen, feed, ...props}) {
  let mentor = props.mentor
  let mentee = props.user

  let displayinfo = [mentee]
  let feedObj = null
  if (mentor !== undefined) {
      displayinfo.push(mentor)
      feedObj = feed[displayinfo[0].id].find((elem) => elem.mentor.id === mentor.id)
      console.log("obj:",feedObj)
  }

  return (
      <Modal
          isOpen={modalOpen}
          onRequestClose={() => { setModalOpen(false) }}
          contentLabel="One small step for man, one giant leap for mankind"
          style={{ content: { zIndex: 20, padding: 0, color: "white" } }}
      >
          <button className='absolute right-6 top-6' onClick={() => { setModalOpen(false) }}>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
          </button>

          <div className="w-full h-full flex flex-row">
              {
                  displayinfo.map((person, index) => {
                      let backgroundClass = 'flex-1 pt-8 flex pl-12 text-white '
                      if(index == 0){
                          // do something
                          backgroundClass += "bg-secondary"
                      }
                      else{
                          // do something
                          backgroundClass += "bg-primary"
                      }
                      
                      return (
                          <div className={backgroundClass}>
                              <ul className='flex flex-col items-start list-disc'>
                                  {/* <img src={person.profile_picture} className="w-28 h-28 rounded-full" /> */}
                                  <div className='flex flex-row items-end mb-4'>
                                      <div className='matchmaking-subheader mr-4'>{person.first_name} {person.last_name}</div>
                                      {person.profile_picture === null ?
                                          <img className="w-28 h-28 rounded-full" src={process.env.PUBLIC_URL + "/blank-profile-picture.png"} alt=''></img>
                                          : <img className="w-28 h-28 rounded-full" src={person.profile_picture} alt='' />}
                                  </div>
                                  <li>
                                      <span className='font-bold'>{person.is_mentee ? "Mentee" : "Mentor"}</span>
                                  </li>
                                  <li>
                                      <span className='font-bold'>Email: </span> 
                                      <span>{person.email}</span>
                                  </li>
                                  <li>
                                      <span className='font-bold'>Bio: </span> 
                                      <span>{person.bio}</span>
                                  </li>
                                  <li>
                                      <span className='font-bold'>Personality traits: </span> 
                                      <span>
                                          <span className={`${feedObj === null ? '' : feedObj.mentorPersonalityMatches.includes(person.personality_1 === null ? null : person.personality_1.toLowerCase()) ? 'text-green-500' : ''}`}>{person.personality_1}, </span>
                                          <span className={`${feedObj === null ? '' : feedObj.mentorPersonalityMatches.includes(person.personality_2 === null ? null : person.personality_2.toLowerCase()) ? 'text-green-500' : ''}`}>{person.personality_2}, </span>
                                          <span className={`${feedObj === null ? '' : feedObj.mentorPersonalityMatches.includes(person.personality_3 === null ? null : person.personality_3.toLowerCase()) ? 'text-green-500' : ''}`}>{person.personality_3}</span>
                                      </span>
                                  </li>

                                  {
                                      person.is_mentee ?
                                          <li>
                                              <span className='font-bold'>Mentor gender preference: </span> 
                                              <span className={`${feedObj === null ? '' : feedObj.mentorGenderPreferenceMatch ? 'text-green-500' : ''}`}>{person.mentor_gender_preference}</span>
                                          </li>
                                          :
                                          <li>
                                              <span className='font-bold'>Gender identity: </span> 
                                              <span className={`${feedObj === null ? '' : feedObj.mentorGenderPreferenceMatch ? 'text-green-500' : ''}`}>{person.gender_identity}</span>
                                          </li>
                                  }

                                  <li>
                                      <span className='font-bold'>{person.is_mentee ? "Career interests: " : "Career experience: "}</span>
                                      <span>{
                                          person.career_interests.map((field, i) => {
                                              if (i == person.career_interests.length - 1) {
                                                  return (<span className={`${feedObj === null ? '' : feedObj.mentorCareerMatches.includes(field.toLowerCase()) ? 'text-green-500' : ''}`}>{field.toLowerCase()}</span>)
                                              }
                                              return (<span>
                                                  <span className={`${feedObj === null ? '' : feedObj.mentorCareerMatches.includes(field.toLowerCase()) ? 'text-green-500' : ''}`}>{field.toLowerCase()}</span>,&nbsp;
                                              </span>)
                                          })
                                      }</span>
                                  </li>
                                  <li>
                                      <span className='font-bold'>Interests: </span>
                                      <span>{
                                          person.interests.map((field, i) => {
                                              if (i == person.interests.length - 1) {
                                                  return (<span className={`${feedObj === null ? '' : feedObj.mentorInterestMatches.includes(field.toLowerCase()) ? 'text-green-500' : ''}`}>{field.toLowerCase()}</span>)
                                              }
                                              return (<span>
                                                  <span className={`${feedObj === null ? '' : feedObj.mentorInterestMatches.includes(field.toLowerCase()) ? 'text-green-500' : ''}`}>{field.toLowerCase()}</span>,&nbsp;
                                              </span>)
                                          })
                                      }</span>
                                  </li>
                                  <li>
                                      <span className='font-bold'>Education: </span>
                                      <span>{
                                          person.education.map((field, i) => {
                                              if (i == person.education.length - 1) {
                                                  return (<span className={`${feedObj === null ? '' : feedObj.mentorEducationMatches.includes(field.toLowerCase()) ? 'text-green-500' : ''}`}>{field.toLowerCase()}</span>)
                                              }
                                              return (<span>
                                                  <span className={`${feedObj === null ? '' : feedObj.mentorEducationMatches.includes(field.toLowerCase()) ? 'text-green-500' : ''}`}>{field.toLowerCase()}</span>,&nbsp;
                                              </span>)
                                          })
                                      }</span>
                                  </li>

                                  {
                                      !person.is_mentee &&
                                      <span className='font-bold'>
                                          Can make {person.num_pairings_can_make === null || person.num_pairings_can_make === 1 ? "1 match" : person.num_pairings_can_make + " matches"}
                                      </span> 
                                  }

                                  {
                                      person.resume === null ? 
                                          <div className='text-white'>No resume</div> : 
                                          <a href={person.resume} target="_blank" className='text-white underline cursor-pointer'>Resume</a>
                                  }
                              </ul>
                          </div>
                      )
                  })
              }
          </div>
      </Modal>
  )
}

export default EntryModal