import React from 'react';
import AddSVG from "../../SVGs/AddSVG"; 

const AddButton = ({rowInfo, onAddClicked, isPersonalTree}) => {
	return (
		<>
			{!isPersonalTree && (
				<button className="buttonNode"
					aria-label="Add Child"
					onClick={() => { 
						onAddClicked(rowInfo);
					}}
				>
					<AddSVG/>
				</button>
			)}
		</>
	);
}

export default AddButton;