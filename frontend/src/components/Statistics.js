import { React, useState } from 'react'
import { Formik, Field, Form } from 'formik'
import axios from 'axios'

function Statistics() {

    const [userResults, setUserResults] = useState({})
    const [eventResults, setEventResults] = useState({})

    return (
        <div className='admin-parent-container'>

            <section id='user'>
                <div className='matchmaking-subheader'>
                    User Lookup
                </div>

                <Formik
                    initialValues={{
                        firstName: '',
                        lastName: '',
                        userid: '',
                        email: '',
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
                            console.log(results)
                        })
                    }}>
                    {({ values }) => (
                        <Form>
                            <div id="my-radio-group">Picked</div>
                            <div role="group" aria-labelledby="my-radio-group">
                                <label>
                                    <Field type="radio" name="picked" value="lookup" />
                                    Lookup
                                </label>
                                <label>
                                    <Field type="radio" name="picked" value="feed" />
                                    Feed for user
                                </label>
                                <label>
                                    <Field type="radio" name="picked" value="feed_all" />
                                    Feed for user (including matches)
                                </label>
                                <div>Picked: {values.picked}</div>
                            </div>
                            <label htmlFor="firstName">First Name</label>
                            <Field id="firstName" name="firstName" placeholder="Jane" />

                            <label htmlFor="lastName">Last Name</label>
                            <Field id="lastName" name="lastName" placeholder="Doe" />

                            <label htmlFor="userid">User ID</label>
                            <Field id="userid" name="userid" placeholder="User ID..." />

                            <label htmlFor="email">Email</label>
                            <Field
                                id="email"
                                name="email"
                                placeholder="jane@acme.com"
                                type="email"
                            />

                            <button type="submit">Submit</button>
                        </Form>
                    )}
                </Formik>
            </section>

            <section id='event'>
                <div className='matchmaking-subheader'>
                    Event Lookup
                </div>
                <Formik
                    initialValues={{
                        startDate: '',
                        startTime: '',
                        endDate: '',
                        endTime: '',
                    }}
                    onSubmit={async (values) => {
                        axios.get("/admin-lookup-user", {
                            params: {
                                "startDate": values.startDate,
                                "startTime": values.startTime,
                                "endDate": values.endDate,
                                "endTime": values.endTime
                            },
                        }).then((results) => {
                            console.log(results)
                        })
                    }}>
                    <Form>
                        <label htmlFor="startDate">Start Date</label>
                        <Field id="startDate" name="startDate" placeholder="Start date" />

                        <label htmlFor="startTime">Start Time</label>
                        <Field id="startTime" name="startTime" placeholder="Start time" />

                        <label htmlFor="endDate">End Date</label>
                        <Field id="endDate" name="endDate" placeholder="End date" />

                        <label htmlFor="endTime">End Time</label>
                        <Field id="endTime" name="endTime" placeholder="End time" />

                        <button type="submit">Submit</button>
                    </Form>
                </Formik>
            </section>

            <section id='match'>
                <div className='matchmaking-subheader'>
                    Match Management
                </div>

                <Formik
                    initialValues={{
                        mentorID: '',
                        menteeID: '',
                    }}
                    onSubmit={async (values) => {
                        axios.post("/admin-delete-match", {
                            "mentorId": values.mentorID,
                            "menteeId": values.menteeID
                        }, {
                            data: {
                                "mentorId": values.mentorID,
                                "menteeId": values.menteeID
                            }
                        }).then((results) => {
                            console.log(results)
                        }).catch(err => {
                            console.log(err)
                        })
                    }}>
                    <Form>
                        <label htmlFor="mentorID">Mentor ID</label>
                        <Field id="mentorID" name="mentorID" placeholder="Mentor ID" />

                        <label htmlFor="menteeID">Mentee ID</label>
                        <Field id="menteeID" name="menteeID" placeholder="Mentee ID" />

                        <button type="submit">Submit</button>
                    </Form>
                </Formik>
            </section>

        </div>
    )
}

export default Statistics