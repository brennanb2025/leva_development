import Modal from 'react-modal'

function EntryModal(props) {
    let mentor = props.mentors
    let mentee = props.user
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
                    [mentee, mentor].map((person) => (
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

export default EntryModal