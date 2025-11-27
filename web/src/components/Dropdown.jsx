import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import './Dropdown.css';

const Dropdown = ({ 
  value, 
  onChange, 
  options = [], 
  disabled = false, 
  placeholder = 'Select...',
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const triggerRef = useRef(null);
  const menuRef = useRef(null);
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0, width: 0, showAbove: false });

  // Calculate menu position when opening or scrolling
  const updateMenuPosition = () => {
    if (triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const viewportWidth = window.innerWidth;
      
      // Estimate dropdown menu height (max-height is 300px from CSS)
      const estimatedMenuHeight = Math.min(300, options.length * 48); // 48px per option (approximate)
      
      // Check if dropdown would go outside viewport at bottom
      const spaceBelow = viewportHeight - rect.bottom;
      const spaceAbove = rect.top;
      
      // Determine if we should show above or below
      let showAbove = false;
      if (spaceBelow < estimatedMenuHeight && spaceAbove > spaceBelow) {
        // Not enough space below, but more space above
        showAbove = true;
      } else if (spaceBelow < estimatedMenuHeight && spaceAbove < estimatedMenuHeight) {
        // Not enough space in either direction, prefer above if more space
        showAbove = spaceAbove > spaceBelow;
      }
      
      // Calculate position
      let top, left, width;
      
      if (showAbove) {
        // Position above the trigger
        top = rect.top - estimatedMenuHeight - 4;
        // Ensure dropdown doesn't go above viewport
        if (top < 4) {
          top = 4;
          // If it still doesn't fit, constrain height
          if (top + estimatedMenuHeight > rect.top - 4) {
            // Can't fit above, try below instead
            showAbove = false;
            top = rect.bottom + 4;
          }
        }
      } else {
        // Position below the trigger (default)
        top = rect.bottom + 4;
        // Ensure dropdown doesn't go below viewport
        if (top + estimatedMenuHeight > viewportHeight - 4) {
          // Try positioning above instead
          if (spaceAbove > estimatedMenuHeight) {
            showAbove = true;
            top = rect.top - estimatedMenuHeight - 4;
          } else {
            // If neither fits well, just constrain to viewport
            top = Math.max(4, viewportHeight - estimatedMenuHeight - 4);
          }
        }
      }
      
      // Ensure dropdown doesn't go outside viewport horizontally
      left = Math.max(4, Math.min(rect.left, viewportWidth - rect.width - 4));
      width = rect.width;
      
      setMenuPosition({
        top,
        left,
        width,
        showAbove
      });
    }
  };

  useEffect(() => {
    if (isOpen) {
      updateMenuPosition();
      
      // Update position on scroll or resize
      window.addEventListener('scroll', updateMenuPosition, true);
      window.addEventListener('resize', updateMenuPosition);
      
      return () => {
        window.removeEventListener('scroll', updateMenuPosition, true);
        window.removeEventListener('resize', updateMenuPosition);
      };
    }
  }, [isOpen]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(event.target) &&
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Find selected option label
  const selectedOption = options.find(opt => {
    if (typeof opt === 'object') {
      return opt.value === value;
    }
    return opt === value;
  });

  const displayValue = selectedOption 
    ? (typeof selectedOption === 'object' ? selectedOption.label : selectedOption)
    : placeholder;

  const handleSelect = (optionValue) => {
    if (onChange) {
      // Create a synthetic event to match native select behavior
      const syntheticEvent = {
        target: { value: optionValue }
      };
      onChange(syntheticEvent);
    }
    setIsOpen(false);
  };

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  return (
    <div 
      className={`custom-dropdown ${disabled ? 'disabled' : ''} ${isOpen ? 'open' : ''} ${className}`}
      ref={dropdownRef}
    >
      <div 
        ref={triggerRef}
        className="dropdown-trigger"
        onClick={handleToggle}
        role="button"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleToggle();
          }
        }}
      >
        <span className={`dropdown-value ${!selectedOption ? 'placeholder' : ''}`}>{displayValue}</span>
        <svg 
          className={`dropdown-arrow ${isOpen ? 'open' : ''}`}
          width="16" 
          height="16" 
          viewBox="0 0 16 16" 
          fill="none"
        >
          <path 
            d="M4 6L8 10L12 6" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          />
        </svg>
      </div>
      {isOpen && createPortal(
        <div 
          ref={menuRef}
          className={`dropdown-menu ${menuPosition.showAbove ? 'dropdown-menu-above' : ''}`}
          style={{
            position: 'fixed',
            top: `${menuPosition.top}px`,
            left: `${menuPosition.left}px`,
            width: `${menuPosition.width}px`
          }}
        >
          {options.map((option, index) => {
            const optionValue = typeof option === 'object' ? option.value : option;
            const optionLabel = typeof option === 'object' ? option.label : option;
            const isSelected = optionValue === value;
            const isDisabled = typeof option === 'object' && option.disabled;

            return (
              <div
                key={index}
                className={`dropdown-option ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
                onClick={() => !isDisabled && handleSelect(optionValue)}
                role="option"
                aria-selected={isSelected}
                aria-disabled={isDisabled}
              >
                {optionLabel}
              </div>
            );
          })}
        </div>,
        document.body
      )}
    </div>
  );
};

export default Dropdown;

