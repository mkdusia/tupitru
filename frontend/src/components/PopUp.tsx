import React, { useState } from 'react';
import '../PopUp.css';
import '../App.css';

interface PopupProps {
  buttonText?: React.ReactNode;
  buttonClassName?: string;
  children: React.ReactNode;
  width?: string;
  height?: string;
}

const Popup: React.FC<PopupProps> = ({
  buttonText,
  buttonClassName,
  children,
  width = '80vw',
  height = '80vh',
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button className={buttonClassName} onClick={() => setIsOpen(true)}>
        {buttonText}
      </button>

      {isOpen && (
        <div className="popup-overlay">
          <div className="popup-content" style={{ width: width, height: height }}>
            <button className="button-close button-circle" onClick={() => setIsOpen(false)}>
              {<img src="/icons/close-x.svg" alt="Close" className="button-icon" />}
            </button>
            {children}
          </div>
        </div>
      )}
    </>
  );
};

export default Popup;
