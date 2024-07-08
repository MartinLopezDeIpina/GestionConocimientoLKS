import Avatar from "@mui/material/Avatar";
import React, { useState } from "react";

export default function UserAvatar({ userName, onClick }) {
  const avatar = stringAvatar(userName);
  const color = stringToColor(userName);

  return (
    <button className="loggedIcon" style={{backgroundColor: color}} onClick={onClick}>
      <p className="loggedIconText">
        {avatar}
      </p>
    </button>
  );
}

function stringToColor(string) {
  let hash = 0;
  let i;

  /* eslint-disable no-bitwise */
  for (i = 0; i < string.length; i += 1) {
    hash = string.charCodeAt(i) + ((hash << 5) - hash);
  }

  let color = "#";

  for (i = 0; i < 3; i += 1) {
    const value = (hash >> (i * 8)) & 0xff;
    color += `00${value.toString(16)}`.slice(-2);
  }
  /* eslint-enable no-bitwise */

  return color;
}

function stringAvatar(name) {
  return name.split(" ").length === 1 ? name.substring(0, 2) : `${name.split(" ")[0][0]}${name.split(" ")[1][0]}`;
}
