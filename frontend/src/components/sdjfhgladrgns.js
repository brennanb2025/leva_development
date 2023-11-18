import { React, useState, useEffect } from 'react'
import Dropdown from 'react-dropdown'
import Modal from 'react-modal'
import axios from 'axios'

function Matchmaking() {

    const [matches, setMatches] = useState([])
    //matches = [{mentee id : [mentor user objects]}]

    const [allMentees, setAllMentees] = useState([])
    //allMentees = [user]
    const [feedMatches, setFeedMatches] = useState({})

    const [numMatches, setNumMatches] = useState({})

    useEffect(() => {

        axios.get("/admin-user-matches", {
            params: {
                "businessId": 1
            },
        }).then((results) => {
            const newDict = {}
            let tempMatches = numMatches
            results.data.map((element) => {
                newDict[element["user"].id] = element["mentors"]
                element["mentors"].map(mentor => {
                    if (numMatches[mentor.id] === undefined) {
                        tempMatches[mentor.id] = 1
                    }
                    else {
                        tempMatches[mentor.id] += 1
                    }
                }) //set user id : [ mentor ]
            })
            setNumMatches(tempMatches)
            setMatches(newDict)
        })

        axios.get("/admin-lookup-users-in-business", {
            params: {
                "businessId": 1
            },
        }).then((results) => {

            const feed = {}
            let filtered = results.data.filter(m => m.is_mentee)
            filtered.map((m) => {
                axios.get("/admin-lookup-user-feed-all", {
                    params: {
                        "userid": m.id
                    },
                }).then((results) => {
                    //setAllUsers(results.data)
                    feed[m.id] = results.data.matches
                    console.log("set feed", feed)
                })
            })
            setFeedMatches(feed)

        })
    }, [])

    //after feed is set, set all mentees
    //have to call admin-lookup-users-in-business twice, sucks, fix later TODO
    useEffect(() => {
        axios.get("/admin-lookup-users-in-business", {
            params: {
                "businessId": 1
            },
        }).then((results) => {
            let filtered = results.data.filter(m => m.is_mentee)
            setAllMentees(filtered)
        })
    }, [feedMatches])

}

export default Matchmaking