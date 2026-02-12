#pragma once

//; C++ Coding Standards Example - Header File
//; This file demonstrates the coding standards for C++ projects.
//; See coding-standards.md for detailed guidelines.

#include <cstdint>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace myproject {

//; Forward declarations for dependencies
class DatabaseConnection;

//; UserRole defines the permission level of a user
//; Used for access control and feature gating
enum class UserRole {
    kGuest,      // Limited access
    kUser,       // Standard access
    kAdmin,      // Administrative access
    kSuperAdmin  // Full system access
};

//; User represents a system user with authentication and profile data
//; This class is thread-safe for read operations
//;@NOTE: Write operations require external synchronization
class User {
public:
    //; Default constructor creates an invalid user
    User() = default;

    //; Constructor with required fields
    //; @param email User's email address (must be unique)
    //; @param name User's display name
    explicit User(const std::string& email, const std::string& name = "");

    //; Destructor
    ~User() = default;

    //; Copy constructor
    User(const User& other) = default;

    //; Copy assignment operator
    User& operator=(const User& other) = default;

    //; Move constructor
    User(User&& other) noexcept = default;

    //; Move assignment operator
    User& operator=(User&& other) noexcept = default;

    //; Getters
    int64_t id() const noexcept { return id_; }
    const std::string& email() const noexcept { return email_; }
    const std::string& name() const noexcept { return name_; }
    UserRole role() const noexcept { return role_; }
    bool isActive() const noexcept { return active_; }

    //; Setters
    void setName(const std::string& name) { name_ = name; }
    void setRole(UserRole role) { role_ = role; }
    void setActive(bool active) { active_ = active; }

    //;@TODO: Add password hashing with bcrypt
    //;@FIXME: Password is stored in plain text (security issue)
    void setPassword(const std::string& password) {
        password_ = password;
    }

    //; Validate returns true if the user has all required fields
    bool Validate() const;

    //; HasPermission checks if user has a specific permission
    bool HasPermission(const std::string& permission) const;

    //; ToJson serializes user to JSON string
    std::string ToJson() const;

    //; FromJson creates a User from JSON string
    //; Returns std::nullopt if parsing fails
    static std::optional<User> FromJson(const std::string& json);

private:
    int64_t id_ = 0;
    std::string email_;
    std::string name_;
    std::string password_;  //;@DEPRECATED: Store hash instead
    UserRole role_ = UserRole::kGuest;
    bool active_ = true;
};

//; UserManager handles user CRUD operations and authentication
//; This class maintains an in-memory cache of users
//;@OPTIMIZE: Consider using a concurrent hash map for better performance
class UserManager {
public:
    //; Constructor takes ownership of the database connection
    explicit UserManager(std::unique_ptr<DatabaseConnection> db);

    //; Destructor
    ~UserManager();

    //; Disable copy (manager owns resources)
    UserManager(const UserManager&) = delete;
    UserManager& operator=(const UserManager&) = delete;

    //; Enable move
    UserManager(UserManager&&) noexcept;
    UserManager& operator=(UserManager&&) noexcept;

    //; CreateUser adds a new user to the system
    //; Returns the ID of the created user, or -1 on failure
    int64_t CreateUser(const User& user);

    //; GetUserById retrieves a user by their ID
    //; Returns std::nullopt if not found
    std::optional<User> GetUserById(int64_t id) const;

    //; GetUserByEmail retrieves a user by their email
    //; Email lookup is case-insensitive
    std::optional<User> GetUserByEmail(const std::string& email) const;

    //; UpdateUser modifies an existing user
    //; Returns true if successful, false if user not found
    bool UpdateUser(const User& user);

    //; DeleteUser removes a user from the system
    //; Returns true if successful, false if user not found
    //;@NOTE: This performs a soft delete (sets active=false)
    bool DeleteUser(int64_t id);

    //; Authenticate validates user credentials
    //; Returns the user if authentication succeeds, std::nullopt otherwise
    std::optional<User> Authenticate(
        const std::string& email,
        const std::string& password) const;

    //; ListUsers returns all users matching the filter criteria
    std::vector<User> ListUsers(
        UserRole role = UserRole::kGuest,
        bool includeInactive = false) const;

    //; RegisterCallback registers a callback for user events
    void RegisterCallback(
        const std::string& event,
        std::function<void(const User&)> callback);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;  // PIMPL idiom
};

//; ValidateEmail checks if the email format is valid
//; Uses a simplified regex check
//;@OPTIMIZE: Could use a more comprehensive regex pattern
bool ValidateEmail(const std::string& email);

//; HashPassword creates a secure hash of the password
//; Uses bcrypt with a random salt
std::string HashPassword(const std::string& password);

//; VerifyPassword checks if password matches the hash
bool VerifyPassword(const std::string& password, const std::string& hash);

//;@DEPRECATED: Use UserManager::CreateUser instead
//; This function will be removed in v2.0
bool CreateUserLegacy(const std::string& email,
                      const std::string& password);

//; UserRoleToString converts UserRole enum to string
const char* UserRoleToString(UserRole role);

//; StringToUserRole parses UserRole from string
//; Returns kGuest if the string is not recognized
UserRole StringToUserRole(const std::string& str);

}  // namespace myproject
