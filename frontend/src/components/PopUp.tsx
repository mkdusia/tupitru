import React from 'react';
import '../PopUp.css';
import { useState } from 'react';
import '../App.css';

interface PopupProps {
  buttonText: string;
  buttonClassName?: string;
  children: React.ReactNode;
}

const Popup: React.FC<PopupProps> = ({ buttonText, buttonClassName, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button className={buttonClassName} onClick={() => setIsOpen(true)}>
        {buttonText}
      </button>

      {isOpen && (
        <div className="popup-overlay">
          <div className="popup-content">
            <button className="button-close button-circle" onClick={() => setIsOpen(false)}>
              X
            </button>
            {children}
          </div>
        </div>
      )}
    </>
  );
};

export default Popup;
