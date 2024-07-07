import '../../../../public/styles/switch.css';

const PersonalTreeSwitch = ({isPersonalTree, switchToggled}) => {
	return (
		<>
			{isPersonalTree && (
				<label className="switch">
					<input type="checkbox" onChange={switchToggled}/>
					<span className="slider round"></span>
				</label>
			)}
		</>
	);
}

export default PersonalTreeSwitch;