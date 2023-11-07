import './App.css';
import { useState, useEffect, memo } from 'react'
import Matchmaking from './components/Matchmaking'

function App() {

  const [isMatch, setIsMatch] = useState(true)

  return (
    <div className='flex flex-col w-full h-screen'>
      <section className="w-full p-8">
        <div className="flex flex-row items-center border-b pb-2">
          <div className="matchmaking-header min-w-[15rem]">{isMatch ? "Matchmaking" : "Statistics"}</div>
          <button className="option-button" onClick={() => { setIsMatch(false) }}>Statistics</button>
          <button className="option-button" onClick={() => { setIsMatch(true) }}>Matchmaking</button>
        </div>
      </section>
      <div className="flex-grow overflow-y-hidden">
        {isMatch ? <Matchmaking /> : <div>SOmething</div>}
      </div>
    </div>
  )
}

export default App;
