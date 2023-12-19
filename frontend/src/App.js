import './App.css';
import { useState, useEffect, memo } from 'react'
import Matchmaking from './components/Matchmaking'
import Statistics from './components/Statistics';

function App() {

  const [isMatch, setIsMatch] = useState(true)

  return (
    <div className='flex flex-col w-full h-screen'>
      <meta name="csrf-token" content="{{ csrf_token() }}" />
      <section className="w-full p-8">
        <div className="flex flex-row items-center border-b pb-2">
          <div className="matchmaking-header min-w-[15rem]">{isMatch ? "Matchmaking" : "User Search"}</div>
          <button className="option-button" onClick={() => { setIsMatch(true) }}>Matchmaking</button>
          <button className="option-button" onClick={() => { setIsMatch(false) }}>User Search</button>
        </div>
      </section>
      <div className="flex-grow">
        {isMatch ? <Matchmaking /> : <Statistics />}
      </div>
    </div>
  )
}

export default App;
