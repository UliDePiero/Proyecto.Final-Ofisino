import * as React from 'react';

export type buttonMap = Record<string, React.ReactElement | string | boolean>;
export type Reservation = {
	id?: number;
	date: Date;
	user?: User;
	boxId?: number;
	box?: Box | null;
	workingSpaceId?: number;
	workingSpace?: WorkingSpace | null;
};
export type Organization = {
	id?: number;
	name: string;
	description: string;
};
export type Building = {
	id?: number;
	organizationId?: number;
	organization?: Organization;
	name: string;
	location: string;
	description: string;
};
export type MeetingRoom = {
	id?: number;
	buildingId?: number;
	building?: Building;
	name: string;
	capacity: number;
	features?: MeetingRoomFeatures;
	description: string;
};
export type OrganizeMeeting = {
	id?: number;
	start: Date;
	end: Date;
	timeStart: Date;
	timeEnd: Date;
	duration: number;
	members: OrganizationMember[];
	description: string;
	summary: string;
	meetingRoomType?: MeetingRoomType;
	features?: MeetingRoomFeatures;
	building?: Building;
};
export type OrganizeMeetingConfirm = {
	start: string;
	end: string;
	duration: number;
	emails: string[];
	meetingRoomType: string;
	meetingRoom?: MeetingRoom;
	meetingRequestId: number;
	kind: string;
	missingFeatures: MeetingRoomFeatures;
	membersConflicts?: OrganizationMember[];
};
export type Meeting = {
	id?: number;
	date: Date;
	duration: number;
	emails: string[];
	description: string;
	summary?: string;
	meetingRoom?: MeetingRoom;
};
export type MeetingRoomFeatures = {
	aireAcondicionado?: number;
	computadoras?: number;
	proyector?: number;
	ventanas?: number;
	sillas?: number;
	mesas?: number;
};
export type WorkingSpace = {
	id?: number;
	buildingId?: number;
	building?: Building;
	name: string;
	area: number;
	squareMetersPerBox: number;
	description: string;
};
export type Box = {
	id?: number;
	workingSpaceId?: number;
	workingSpace?: WorkingSpace;
	name: string;
	description?: string;
};
export type User = {
	id?: number;
	name: string;
	avatarUrl?: string;
	email: string;
	domainId: string;
};
export type MeetingRoomType = {
	code: string;
	name: string;
};
export type OrganizationMember = {
	email: string;
	name: string;
};
export type LoginContext = {
	email: string;
	setEmail: (email: string) => void;
	userId: number;
	setUserId: (userId: number) => void;
	clientId: string;
	isLoggedIn: boolean;
	setIsLoggedIn: (isLogged: boolean) => void;
	isAdmin: boolean;
	setIsAdmin: (isLogged: boolean) => void;
	officeInstance?: any;
	setOfficeInstance?: (officeInstance: any) => void;
	setAvatarUrl?: (avatarUrl: string) => void;
	avatarUrl?: string;
	setName?: (name: string) => void;
	name?: string;
};
