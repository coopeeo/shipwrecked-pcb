try:
    from typing import List, Optional
except ImportError:
    # we're on an MCU, typing is not available
    pass

import json
import logging

class Contact:
    """
    Represents a contact.
    """
    def __init__(self, name: str, pronouns: str, badge_id: str, handle: str):
        self.name = name
        self.pronouns = pronouns
        self.badge_id = badge_id
        self.handle = handle

    def __repr__(self):
        return f"Contact(name={self.name}, pronouns={self.pronouns}, badge_id={self.badge_id})"
    
    def to_dict(self):
        """
        Convert the contact to a dictionary representation.
        """
        return {
            'name': self.name,
            'pronouns': self.pronouns,
            'badge_id': self.badge_id,
            'handle': self.handle
        }

class ContactsManager:
    """
    A database of mappings between names, pronouns and badge IDs.
    """
    def __init__(self, contacts_file: str = "/contacts.json"):
        self.logger = logging.getLogger("ContactsManager")
        self.logger.setLevel(logging.INFO)

        try:
            with open(contacts_file, 'r') as f:
                json.load(f)  # Validate JSON format
        except OSError as e:
            if e.errno == 2:  # File not found
                self.logger.warning(f"Contacts file not found: {contacts_file}. Creating a new one.")
                with open(contacts_file, 'w') as f:
                    json.dump([], f)
            else:
                self.logger.error(f"Error reading contacts file: {e}. Resetting to empty contacts.")
                with open(contacts_file, 'w') as f:
                    json.dump([], f)
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON format in contacts file: {contacts_file}. Resetting to empty contacts.")
            with open(contacts_file, 'w') as f:
                json.dump([], f)

        self.contacts_file = contacts_file
        self.contacts = self.load_contacts()

    def load_contacts(self) -> List[Contact]:
        """
        Load contacts from the JSON file.
        """
        try:
            with open(self.contacts_file, 'r') as f:
                contacts_data = json.load(f)
                return [Contact(**contact) for contact in contacts_data]
        except Exception as e:
            self.logger.error(f"Error loading contacts: {e}")
            return []

    def save_contacts(self) -> None:
        """
        Save contacts to the JSON file.
        """
        try:
            with open(self.contacts_file, 'w') as f:
                json.dump([contact.to_dict() for contact in self.contacts], f)
        except Exception as e:
            self.logger.error(f"Error saving contacts: {e}")

    def add_contact(self, name: str, pronouns: str, badge_id: str, handle: str) -> None:
        """
        Add a new contact to the contacts list.
        """
        new_contact = Contact(name=name, pronouns=pronouns, badge_id=badge_id, handle=handle)
        self.contacts.append(new_contact)
        self.save_contacts()

    def get_contact_by_badge_id(self, badge_id: str) -> Optional[Contact]:
        """
        Get a contact by their badge ID.
        """
        for contact in self.contacts:
            if contact.badge_id == badge_id:
                return contact
        return None
    
    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """
        Get a contact by their name.
        """
        for contact in self.contacts:
            if contact.name.lower() == name.lower():
                return contact
        return None
    
    def remove_contact_by_badge_id(self, badge_id: str) -> bool:
        """
        Remove a contact by their badge ID.
        :return: True if the contact was removed, False if not found.
        """
        for i, contact in enumerate(self.contacts):
            if contact.badge_id == badge_id:
                del self.contacts[i]
                self.save_contacts()
                return True
        return False
    
    def remove_contact_by_name(self, name: str) -> bool:
        """
        Remove a contact by their name.
        :return: True if the contact was removed, False if not found.
        """
        for i, contact in enumerate(self.contacts):
            if contact.name.lower() == name.lower():
                del self.contacts[i]
                self.save_contacts()
                return True
        return False
    
    def get_all_contacts(self) -> List[Contact]:
        """
        Get a list of all contacts.
        """
        return self.contacts.copy()