import { React, useState } from 'react'
import { Formik, Field, Form } from 'formik'
import axios from 'axios'
import DatePicker from 'react-datepicker'
import { DatePickerField } from './DatePickerField'
import Modal from 'react-modal'

function Statistics() {

    const [userResults, setUserResults] = useState([])
    const [eventResults, setEventResults] = useState([])
    const [deleteResults, setDeleteResults] = useState()
    const [modalOpen, setModalOpen] = useState(false)
    const [currentQuery, setCurrentQuery] = useState("")

    const handleSubmitForm = (values) => {
        axios.get("/csrf", { withCredentials: true }).then((response) => {
            axios.post("/admin-delete-match", {
                mentorId: values.mentorID,
                menteeId: values.menteeID
            }, {
                withCredentials: true,
                headers: {
                    'X-CSRFToken': response.headers['x-csrftoken'],
                    'Content-Type': 'multipart/form-data'
                }
            }).then((results) => {
                console.log(results)
                setDeleteResults(results)
            }).catch(err => {
                console.log(err)
            })
        })
    }

    function UserModal() {
        let person = userResults[0]
        return (
            <Modal
                isOpen={modalOpen}
                onRequestClose={() => { setModalOpen(false) }}
                contentLabel="One small step for man, one giant leap for mankind"
                style={{ content: { zIndex: 20 } }}
            >
                <button onClick={() => { setModalOpen(false) }}>Close</button>

                <div className='w-full flex flex-col justify-center items-center'>
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
            </Modal>
        )
    }

    return (
        <div className='admin-parent-container items-center pb-4'>

            <section id='user' className='stats-section'>
                <div className='matchmaking-subheader'>
                    Search User
                </div>

                <Formik
                    initialValues={{
                        firstName: '',
                        lastName: '',
                        userid: '',
                        email: '',
                        picked: 'lookup'
                    }}
                    onSubmit={async (values) => {
                        let url = ""

                        if (values.picked === "lookup") {
                            url = "/admin-lookup-user"
                        }
                        else if (values.picked === "feed") {
                            url = "/admin-lookup-user-feed"
                        }
                        else if (values.picked === "feed_all") {
                            url = "admin-lookup-user-feed-all"
                        }

                        axios.get(url, {
                            params: {
                                "userId": values.userid,
                                "firstName": values.firstName,
                                "lastName": values.lastName,
                                "email": values.email
                            },
                        }).then((results) => {
                            console.log("results here");
                            console.log(results);
                            setUserResults(results.data)
                        })
                        setCurrentQuery(values.picked)
                    }}>
                    {({ values }) => (
                        <Form>
                            <div role="group" aria-labelledby="my-radio-group" className='flex flex-col mt-4'>
                                <label className='regtext'>
                                    Lookup
                                    <Field type="radio" name="picked" value="lookup" className="radio-button" />
                                    <span className="checkmark"></span>
                                </label>
                                <label className='regtext'>
                                    User Potential Matches
                                    <Field type="radio" name="picked" value="feed" className="radio-button" />
                                    <span className="checkmark"></span>
                                </label>
                                <label className='regtext'>
                                    User Confirmed Matches
                                    <Field type="radio" name="picked" value="feed_all" className="radio-button" />
                                    <span className="checkmark"></span>
                                </label>
                            </div>

                            <div className='flex flex-row mt-4'>
                                <div className='input-container'>
                                    <label htmlFor="firstName">First Name</label>
                                    <Field id="firstName" name="firstName" placeholder="Jane" className="stats-input" />
                                </div>

                                <div className='input-container'>
                                    <label htmlFor="lastName">Last Name</label>
                                    <Field id="lastName" name="lastName" placeholder="Doe" className="stats-input" />
                                </div>

                                <div className='input-container'>
                                    <label htmlFor="userid">User ID</label>
                                    <Field id="userid" name="userid" placeholder="User ID..." className="stats-input" />
                                </div>

                                <div className='input-container'>
                                    <label htmlFor="email">Email</label>
                                    <Field
                                        id="email"
                                        name="email"
                                        placeholder="jane@acme.com"
                                        type="email"
                                        className="stats-input"
                                    />
                                </div>
                            </div>

                            <button type="submit" className='submit-button'>Search</button>

                            {userResults.length > 0 && currentQuery === "lookup" ? (
                                <div className='bg-slate-500 rounded-md p-4 text-white mt-4 w-fit flex flex-row items-center hover:cursor-pointer'
                                    onClick={() => { setModalOpen(true) }}>
                                    <img src={userResults[0].profile_picture} className='h-16 w-auto rounded-full' />
                                    <div className='ml-4'>
                                        <div>Name: {userResults[0].first_name} {userResults[0].last_name}</div>
                                        <div>
                                            Email: {userResults[0].email}
                                        </div>
                                        <div>
                                            Occupation: {userResults[0].current_occupation}
                                        </div>
                                        <div>
                                            Division: {userResults[0].division}
                                        </div>
                                    </div>
                                </div>
                            ) : ""}

                            {userResults.length > 0 && currentQuery != "lookup" ? (
                                <div className='bg-slate-500 rounded-md p-4 text-white mt-4 w-fit flex flex-row items-center hover:cursor-pointer'
                                >
                                    {
                                        JSON.stringify(userResults)
                                    }
                                </div>
                            ) : ""}

                            {userResults.length > 0 ? <UserModal /> : ""}
                        </Form>
                    )}
                </Formik>

            </section>

            <section id='match' className='stats-section'>
                <div className='matchmaking-subheader'>
                    Delete Match
                </div>

                <Formik
                    initialValues={{
                        mentorId: '',
                        menteeId: '',
                    }}
                    onSubmit={(values) => handleSubmitForm(values)}>
                    <Form>
                        <div className='flex flex-row'>
                            <div className='input-container'>
                                <label htmlFor="mentorId">Mentor ID</label>
                                <Field id="mentorId" name="mentorId" placeholder="mentor ID" className="stats-input" />
                            </div>

                            <div className='input-container'>
                                <label htmlFor="menteeId">Mentee ID</label>
                                <Field id="menteeId" name="menteeId" placeholder="Mentee ID" className="stats-input" />
                            </div>
                        </div>

                        <button type="submit" className='submit-button'>Delete</button>
                    </Form>
                </Formik>

                <div className='mt-4'>
                    {
                        deleteResults ?
                            (<span>
                                {deleteResults.data.success ?
                                    <span className='text-green-500'>Success!</span> :
                                    <span className='text-red-700'>Failed...</span>}
                            </span>)
                            : ""
                    }
                </div>
            </section>

        </div>
    )
}

export default Statistics