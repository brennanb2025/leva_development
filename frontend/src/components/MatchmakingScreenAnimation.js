import React from 'react';
import './MatchmakingScreenAnimation.css';

const MatchmakingScreen = ({ animationVisible }) => {
    const welcomeRef = React.createRef();

  return (
    <React.Fragment>
      {animationVisible && (
        <div className="intro-animation" ref={welcomeRef}>
          <div className="text-container">
            Matches submitted!
          </div>
        </div>
      )}
    </React.Fragment>
  );
};

export default MatchmakingScreen;
